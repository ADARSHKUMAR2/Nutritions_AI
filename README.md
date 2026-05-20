# Breakfast Planner

AI-powered breakfast planning app that generates healthy meal ideas, estimates calories, checks ingredient prices, and can export a summary deck to Google Slides.

## Features

- Streamlit UI for interactive breakfast plan generation
- Multi-agent workflow using `openai-agents`
- Local nutrition lookup using ChromaDB
- Web-backed ingredient price lookup with Exa
- Guardrails to keep prompts food-related
- Optional Google Slides export for final recommendations

## Project Structure

- `Nutrition_Proj/app.py` - Streamlit app entrypoint
- `Nutrition_Proj/main.py` - CLI test runner for the advisor agent
- `Nutrition_Proj/agent_factory.py` - agent definitions and orchestration
- `Nutrition_Proj/db.py` - ChromaDB + calorie and web search tools
- `Nutrition_Proj/slides_tool.py` - Google Slides tool integration
- `pyproject.toml` - dependencies and project metadata

## Prerequisites

- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/) installed
- API keys:
  - `OPENAI_API_KEY` (used with GitHub/Azure model endpoint in this project)
  - `EXA_API_KEY`
  - `LANGSMITH_API_KEY` (optional but recommended for tracing)

## Setup

From the repository root:

```bash
uv sync
```

Create a `.env` file (or export these in your shell):

```env
OPENAI_API_KEY=your_key_here
EXA_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
LANGSMITH_TRACING=true
```

## Run the App

The Streamlit app is inside `Nutrition_Proj`, so run:

```bash
cd Nutrition_Proj
uv run streamlit run app.py
```

## Run the CLI Flow

```bash
cd Nutrition_Proj
uv run main.py
```

## Google Slides Export Setup (Optional)

The slides tool expects Google OAuth client credentials in:

- `Nutrition_Proj/credentials.json`

On first run, OAuth will open in browser and create:

- `Nutrition_Proj/token.json`

If scopes change, delete `token.json` and authenticate again.

## How It Works

`breakfast_advisor_guarded_agent` orchestrates:

1. `breakfast_planner` tool to create healthy options
2. `calorie_calculator` tool for nutrition estimates
3. `price_checker` tool for ingredient pricing
4. `generate_breakfast_deck` tool for Slides export

Final output is returned in a structured response (`AdvisorResponse`) with markdown text plus chart data for Streamlit visualization.

## Troubleshooting

- **Rate limit / model errors**: verify `OPENAI_API_KEY` and model access.
- **Search failures**: check `EXA_API_KEY`.
- **Slides creation fails**: ensure `credentials.json` is valid and OAuth completed.
- **No nutrition results**: confirm ChromaDB data exists in `Nutrition_Proj/chroma`.
