
# AI Development Report
## AI Sales Intelligence Assistant

### 1. Project Overview
The AI Sales Intelligence Assistant is a mini business intelligence application that answers natural-language questions about sales data. It uses Python, SQLite, FastAPI, Streamlit, and a locally running language model.

### 2. AI Tools Used
- **ChatGPT:** Assisted with project planning, code development, debugging, test preparation, and documentation.
- **Ollama with Llama 3.2 1B:** Used locally to interpret natural-language business questions and identify supported analytics operations.

### 3. How AI Assistance Was Used
AI assistance supported:
- Designing the project structure and workflow.
- Developing and debugging Python application components.
- Connecting the FastAPI backend to the Streamlit interface.
- Preparing automated analytics tests.
- Writing project documentation and explaining technical decisions.

### 4. Data Processing and Analytics
The application imports sales records from a CSV file into SQLite. Python and SQL perform the analytical calculations.

The revenue calculation includes eligible completed transactions with valid dates, positive quantities, known non-negative unit prices, and non-negative discounts. Returned or otherwise ineligible transactions are excluded from revenue totals.

For the supplied dataset, the application reported:
- Total source records: 51
- Eligible transactions: 48
- Eligible revenue: 1,439,200

### 5. Architecture and Reliability
The local language model helps interpret the user's question. Predefined Python analytics functions then retrieve and calculate results from the database.

This separation helps keep analytical results deterministic and reduces reliance on generated numerical answers. The analytics query helper uses read-only database access.

### 6. Testing
Five automated analytics tests passed during development:
1. Total revenue calculation.
2. Top product identification.
3. Monthly revenue retrieval.
4. Top region identification.
5. Month-to-month revenue comparison.

The tests were run using `python -m pytest tests/test_analytics.py -v`.

### 7. Limitations
- Ollama and the required local model must be installed and running.
- The assistant supports a defined set of analytics questions, not every possible business question.
- Ambiguous questions may be interpreted incorrectly.
- Results depend on the completeness and quality of the source data.
- The project is a prototype and needs further security, scalability, and monitoring work before production use.

### 8. Human Review and Responsibility
AI-generated suggestions and code were reviewed and tested during development. The developer remains responsible for validating the implementation, confirming analytical results, and ensuring that the final submission meets the assessment requirements.

### 9. Conclusion
This project demonstrates how local language-model interpretation can be combined with deterministic Python and SQL analytics to create an accessible business intelligence assistant.

