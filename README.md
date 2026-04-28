<div align="center">
  <img src="Deep-Gabriel.png" alt="Deep-Gabriel Logo" width="200"/>
  <h1>Deep-Gabriel</h1>
</div>

## Overview

Deep-Gabriel is an autonomous multi-agent research pipeline that orchestrates complex, deep-dive web research using state-of-the-art Large Language Models. Leveraging LangGraph and DeepSeek, it decomposes complex user queries into sub-topics, conducts parallel multi-threaded research through specialized agents, and compiles comprehensive, fully-formatted reports.

<div align="center">
  <img src="deep-gabriel-demo.gif" alt="Deep-Gabriel Demo" width="800"/>
</div>

## Architecture

Deep-Gabriel uses a robust supervisor-worker architecture:
- **Scoping Agent**: Analyzes user queries and determines if clarification is needed before generating a comprehensive research brief.
- **Supervisor Agent**: Deconstructs the research brief into discrete topics, delegates them to researcher agents, and coordinates the overall workflow to ensure maximum depth and coverage.
- **Researcher Agents**: Specialized agents that use tool calling to navigate the web, summarize documents, and synthesize insights without hitting rate limits or context window restrictions.
- **Report Generation**: Aggregates all insights into a polished, downloadable DOCX document, properly formatted with native LaTeX math and markdown support.

## Features
- **Parallel Execution**: Conducts independent research threads simultaneously.
- **Automated DocX Generation**: Produces well-structured, print-ready documents out-of-the-box.
- **DeepSeek Integration**: Uses the highly capable DeepSeek language models to evaluate search results and draw conclusions.
- **Gradio Interface**: Provides a clean, modern web interface for users to enter prompts and download their final papers.

## Getting Started

1. Ensure dependencies are installed and the environment is configured.
2. Provide your `DEEPSEEK_API_KEY` in the `.env` file.
3. Run the application:
   ```bash
   python main.py
   ```
4. Enter your research topic in the interface and click **Generate Research Paper**.

## Built With
- LangChain & LangGraph
- DeepSeek
- Gradio
- python-docx
