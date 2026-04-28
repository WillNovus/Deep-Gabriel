import gradio as gr
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env variables including DEEPSEEK_API_KEY
load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from agents.state_scope import AgentState, AgentInputState
from agents.research_agent_scope import write_research_brief
from agents.multi_agent_supervisor import supervisor_agent
from agents.research_agent_full import final_report_generation
from docx_compiler import generate_docx_from_state

# We bypass clarify_with_user so we can take the user's query and directly convert it to a research brief.
auto_research_builder = StateGraph(AgentState, input_schema=AgentInputState)
auto_research_builder.add_node("write_research_brief", write_research_brief)
auto_research_builder.add_node("supervisor_subgraph", supervisor_agent)
auto_research_builder.add_node("final_report_generation", final_report_generation)

auto_research_builder.add_edge(START, "write_research_brief")
auto_research_builder.add_edge("write_research_brief", "supervisor_subgraph")
auto_research_builder.add_edge("supervisor_subgraph", "final_report_generation")
auto_research_builder.add_edge("final_report_generation", END)

auto_agent = auto_research_builder.compile()

async def run_pipeline(query: str):
    if not query.strip():
        yield "Please provide a query", "Waiting for input...", None
        return

    try:
        # State begins with a human message representing the query
        inputs = {"messages": [HumanMessage(content=query)]}
        config = {"recursion_limit": 50}
        
        log_text = f"🚀 **Starting auto research agent for query:** {query}\n"
        yield "", log_text, None
        
        final_state = None
        
        # Using astream_events to catch detailed execution events
        async for event in auto_agent.astream_events(inputs, config=config, version="v2"):
            kind = event["event"]
            name = event.get("name", "")
            
            # Identify the stage
            if kind == "on_chain_start":
                if name in ["write_research_brief", "supervisor_subgraph", "final_report_generation"]:
                    log_text += f"\n🔄 **Stage**: {name}...\n"
                    yield "", log_text, None
                    
            # Identify tool usage
            elif kind == "on_tool_start":
                log_text += f"  ↳ 🛠️ **Tool in use**: {name}\n"
                yield "", log_text, None
                
            elif kind == "on_tool_end":
                if name == "ConductResearch":
                    log_text += f"  ↳ ✅ **Sub-agent research completed**\n"
                    yield "", log_text, None
                
            # Grab the final state from the main graph completion
            elif kind == "on_chain_end" and name == "LangGraph":
                final_state = event["data"].get("output")
        
        # Fallback if astream_events didn't capture the final state output directly
        if not final_state:
            final_state = await auto_agent.ainvoke(inputs, config=config)

        log_text += "\n📝 **Research finished, compiling docx...**\n"
        yield "", log_text, None
        
        final_report = final_state.get("final_report", "No report generated.")
        
        # docx_compiler expects "final_paper" or "final_draft".
        final_state["final_paper"] = final_report
        final_state["topic"] = query
        
        filename, docx_bytes = generate_docx_from_state(final_state)
        
        out_path = f"/tmp/{filename}"
        with open(out_path, "wb") as f:
            f.write(docx_bytes)
            
        log_text += f"🎉 **Generated docx at:** {out_path}\n"
        yield final_report, log_text, out_path
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield f"Error: {str(e)}", "An error occurred.", None

with gr.Blocks(title="Deep Gabriel") as demo:
    with gr.Row():
        gr.Image("Deep-Gabriel.png", height=80, width=80, show_label=False, container=False, min_width=80)
        gr.Markdown("# Deep Gabriel")
    gr.Markdown("Enter a query below. The system will orchestrate web research using DeepSeek and Tavily, then compile a final DOCX file for you to download.")
    
    with gr.Row():
        query_input = gr.Textbox(label="Research Topic", placeholder="Enter your research topic...", lines=2)
    
    submit_btn = gr.Button("Generate Research Paper")
    
    with gr.Row():
        with gr.Column(scale=1):
            progress_output = gr.Markdown(label="Agent Progress / Logs", value="Waiting for input...")
        with gr.Column(scale=2):
            report_output = gr.Markdown(label="Generated Report Preview")
            file_output = gr.File(label="Download finalized DOCX")
            
    submit_btn.click(fn=run_pipeline, inputs=query_input, outputs=[report_output, progress_output, file_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
