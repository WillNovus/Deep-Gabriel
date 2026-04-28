# Agents: Technical Overview

This `agents/` module powers the core intelligence and orchestration of the Deep-Gabriel research pipeline. It utilizes **LangGraph** to model the research process as a state machine, orchestrating a team of specialized AI agents.

## Multi-Agent Architecture

The orchestration is divided into three distinct phases, each handled by specialized agents or subgraphs:

### 1. Scoping Agent (`research_agent_scope.py`)
**Purpose**: To refine and structure the user's initial query into a highly specific research brief.
- **Workflow Node**: `write_research_brief`
- **Mechanism**: Takes the raw input prompt and uses a structured output model (`method="function_calling"`) to translate it into a formalized `ResearchQuestion` schema. 
- **State Output**: Emits the generated `research_brief` which serves as the foundational instruction for the rest of the pipeline.

### 2. Supervisor Agent (`multi_agent_supervisor.py`)
**Purpose**: To coordinate the actual deep research process by delegating specific tasks and maintaining a global context.
- **Workflow Nodes**: `supervisor` -> `supervisor_tools`
- **Mechanism**: 
  - The supervisor runs in a loop up to a predefined limit (`max_researcher_iterations`).
  - It uses a `think_tool` to strategically reflect on the current progress and identify knowledge gaps.
  - It triggers parallel `ConductResearch` tool calls, spawning independent **Researcher Agents**.
  - It evaluates all returned notes and decides whether to continue researching or mark the research as complete.

### 3. Researcher Agents (`research_agent.py`)
**Purpose**: To autonomously browse the web, scrape content, and synthesize findings for a single, focused sub-topic.
- **Workflow Nodes**: `researcher_tools` -> `researcher_think`
- **Mechanism**: 
  - Spawned asynchronously by the Supervisor, these agents run their own independent state graphs.
  - They execute targeted queries via the `tavily_search` tool to fetch web data.
  - They process large volumes of raw text and compress the insights down into concise notes using their context window.
  - Returns the condensed data back to the Supervisor to avoid blowing up the global context limit.

### 4. Report Generation (`research_agent_full.py`)
**Purpose**: To synthesize all aggregated research notes into a final, cohesive document.
- **Workflow Node**: `final_report_generation`
- **Mechanism**: Takes the `raw_notes` and `supervisor_messages` and formats them into a comprehensive markdown paper. It organizes the information into logical sections, ensuring all findings from the parallel research threads are effectively summarized and contextualized.

## State Management

The entire flow is managed through shared state dictionaries (`AgentState` and `SupervisorState`), which map inputs, outputs, and intermediate data across nodes seamlessly using LangGraph. This ensures that context (like the `research_brief` or accumulated `notes`) persists correctly through asynchronous multi-agent communication.
