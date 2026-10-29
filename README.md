
# AI Sales Intelligence Assistant

A Mini AI Business Intelligence Assistant that answers natural-language questions about sales data using a local Large Language Model (LLM), Python analytics, SQLite, and FastAPI. A Streamlit interface allows users to ask questions and view results.

## Features

- Loads sales data from a CSV file into SQLite.
- Cleans and validates data before calculating revenue.
- Uses a local LLM (Ollama with Llama 3.2 1B) to interpret business questions.
- Uses predefined Python analytics functions for reliable calculations.
- Provides a FastAPI endpoint for natural-language questions.
- Includes a Streamlit interface for interactive use.
- Handles unsupported questions and invalid month comparisons.
- Includes automated tests for core analytics functions.

## Technology Stack

- Python
- Pandas
- SQLite
- FastAPI
- Ollama (Llama 3.2 1B)
- Streamlit
- Pytest

## Project Structure

```text
AI_Sales_Intelligence_Assistant/
├── app/
│   ├── main.py
│   ├── analytics.py
│   ├── database.py
│   ├── inspect_data.py
│   └── streamlit_app.py
├── data/
│   ├── ai_bi_assistant_sales_data - GET.csv
│   └── sales.db
├── tests/
│   └── test_analytics.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup Instructions

### 1. Prerequisites

Install Python, Git, and Ollama. The application uses the locally installed Llama 3.2 1B model.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
pip install pytest
```

### 4. Download the local model

```powershell
ollama pull llama3.2:1b
```

Ensure the Ollama application/service is running.

### 5. Prepare the database

From the project root, run:

```powershell
python app/database.py
```

This loads the CSV data into the SQLite database. Run this step when setting up the project for the first time.

### 6. Start the FastAPI backend

Open a terminal in the project root and run:

```powershell
uvicorn main:app --app-dir app --reload
```

API documentation is available at:

http://127.0.0.1:8000/docs

### 7. Start the Streamlit interface

Open a second terminal, activate the same virtual environment, and run:

```powershell
streamlit run app/streamlit_app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501.

## Example Business Questions

1. What is the total revenue?
2. Which product generated the most revenue?
3. Show monthly revenue.
4. Which region has the highest sales?
5. Compare revenue between 2026-01 and 2026-02.

## Data Quality and Revenue Calculation

The application retains the imported records and applies data-quality checks before calculating revenue. Revenue is calculated only for eligible completed transactions with valid dates, positive quantities, known non-negative unit prices, and non-negative discounts.

Returned transactions and transactions that do not meet the revenue eligibility conditions are excluded from revenue totals. Missing or invalid values should not be silently treated as valid revenue.

## Architecture

1. **CSV input:** The sales dataset is read using Pandas.
2. **Data preparation:** Data is cleaned, validated, and loaded into SQLite.
3. **User interface:** Streamlit accepts a natural-language business question.
4. **API:** FastAPI receives the question through the `/ask` endpoint.
5. **AI interpretation:** Ollama's local LLM classifies the question into a supported intent.
6. **Analytics:** Python functions execute predefined, read-only SQL queries against SQLite.
7. **Response:** The API returns a structured answer, which Streamlit displays.

The LLM selects the intended analytics operation; Python controls execution. The model does not directly execute generated SQL.

## API

### Health check

`GET /health`

### Ask a business question

`POST /ask`

Example request:

```json
{
  "question": "Which product generated the most revenue?"
}
```

The API returns the question, detected intent, and structured answer when the request is supported.

## Automated Tests

Run the tests from the project root:

```powershell
python -m pytest tests/test_analytics.py -v
```

The analytics tests cover total revenue, top product, monthly revenue, top region, and month comparison.

## Limitations

- The assistant supports a defined set of sales analytics questions rather than arbitrary business questions.
- AI interpretation can occasionally misclassify ambiguous questions.
- The local model must be installed and running.
- Results depend on the quality and completeness of the input dataset.
- The current application is a prototype and has not been designed for production-scale deployment.

## AI-Assisted Development

A local LLM was used to interpret natural-language business questions. AI assistance was also used during development to help structure the application, debug errors, write tests, and prepare documentation. Core calculations are performed by deterministic Python analytics functions and read-only database queries.

All generated code and outputs should be reviewed and tested before use.

## Future Improvements

- Add more supported business questions.
- Improve intent classification and validation.
- Add charts, filters, and export options.
- Expand automated API and invalid-input tests.
- Improve deployment, logging, and security.

## Author

Developed as part of the RSG AI-Assisted Development Challenge.
