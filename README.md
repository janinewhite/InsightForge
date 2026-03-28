# InsightForge

InsightForge is a runnable Streamlit business intelligence assistant for Windows 11. It analyzes structured sales data, retrieves relevant statistics, generates charts, maintains conversation memory, and optionally uses an OpenAI model for richer narrative summaries.

## Features

- Streamlit chat interface
- CSV/XLSX upload or bundled sample dataset
- Structured analytics over:
  - sales trends over time
  - product performance
  - regional analysis
  - customer segmentation by age and gender
  - customer satisfaction
  - summary statistics
- Agentic routing that chooses the right analysis tool based on the user query
- Session memory for follow-up questions
- Local SQLite logging for conversations and evaluations
- Optional LLM summaries with OpenAI
- Evaluation script with optional QAEvalChain support

## Project structure

```text
insightforge_project/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── sales_data.csv
├── storage/
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── charts.py
│   ├── config.py
│   ├── data_loader.py
│   ├── evaluator.py
│   ├── logger.py
│   ├── memory.py
│   ├── metric_engine.py
│   ├── prompts.py
│   └── retriever.py
└── tests/
    └── test_metrics.py
```

## How to run the project on Windows 11

### Install Python 3.11 or 3.12.
  Python 3.11.9 installed for this project from https://www.python.org/downloads/. Checked Add Python to PATH when installing.
  Verified version with python --version in Powershell.

### Enable OpenAI access
  Copy or rename .env.example to .env
  Add you API key to .env. Open AI keys can be created at https://platform.openai.com/api-keys.
    OPENAI_API_KEY=your_key_here

### Run the app using Powershell
  Open PowerShell in the folder.
  Change directory to the project folder.
    cd "<project path>"
  Establish Python environment.
    python -m venv .venv
    .venv\Scripts\Activate.ps1
      If there is  security error run the following commnd, then repeat the activation.
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
        .venv\Scripts\Activate.ps1
  Install required Python packages.
    pip install --upgrade pip
    pip install -r requirements.txt
  Enable OpenAI API access. Edit .env 
  Run the app.
    streamlit run app.py

## What the app can answer

The app can run without an API key. In that case it uses deterministic rule-based business summaries.

- Which product drives the most revenue?
- Which region is underperforming?
- Show the sales trend over time.
- Segment customers by age or gender.
- What is the median or standard deviation of sales?
- How does customer satisfaction vary by product or region?

## Evaluation

Run comand in Powershell.
  python -m src.evaluator

This creates or updates entries in the local SQLite database under `storage/insightforge.db`.

If you have an OpenAI key configured and compatible LangChain packages installed, the evaluator will also attempt a QAEvalChain-based grading pass.

## Notes

- The dataset is treated as pre-prepared, matching the capstone requirement.
- The retriever is deliberately structured for tabular BI use cases rather than general document search.
- Session memory is stored in Streamlit state and persisted to SQLite logs.
