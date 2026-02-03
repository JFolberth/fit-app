# fit-app Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-21

## Active Technologies
- Python 3.11 (Azure Functions) + vanilla JS (frontend) + Azure Functions Python, Pydantic validation (backend), Playwright (tests), MCP client SDK (Python, for remote MCP server communication via Streamable HTTP/SSE), Azure AI Foundry SDK (azure-ai-inference or azure-ai-projects), Azure Identity SDK (for managed identity) (002-ai-homepage-coach)
- Azure Cosmos DB (activities container, accessed via remote MCP server) (002-ai-homepage-coach)

- [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION] + [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION] (001-activity-tracking)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

[e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]: Follow standard conventions

## Recent Changes
- 002-ai-homepage-coach: Added Python 3.11 (Azure Functions) + vanilla JS (frontend) + Azure Functions Python, Pydantic validation (backend), Playwright (tests), MCP client SDK (Python, for remote MCP server communication via Streamable HTTP/SSE), Azure AI Foundry SDK (azure-ai-inference or azure-ai-projects), Azure Identity SDK (for managed identity)

- 001-activity-tracking: Added [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION] + [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

<!-- MANUAL ADDITIONS START -->

## Git Operations

- **Do NOT commit or push code automatically.** Always let the user review changes before committing.
- When making code changes, only edit the files. Do not run `git commit` or `git push` commands.
- The user will commit and push changes when they are ready.

<!-- MANUAL ADDITIONS END -->
