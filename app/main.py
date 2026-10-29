import json
import ollama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


from analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months,
)

app = FastAPI(
    title="AI Sales Intelligence Assistant",
    description="Ask questions about sales data and get database-backed answers.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)

    
def interpret_question(question: str):
    """Use a local LLM to interpret a business question safely."""
    prompt = f"""
Classify the sales question into one intent.

Return JSON with keys: intent, month1, month2.

Allowed intents:
total_revenue, top_product, monthly_revenue,
top_region, month_comparison, unknown

Rules:
- "Which product generated the most revenue?" means top_product.
- "What is the total revenue?" means total_revenue.
- "Show monthly revenue" means monthly_revenue.
- "Which region has the highest sales?" means top_region.
- "Compare revenue between 2026-01 and 2026-02" means month_comparison.
- For month_comparison, extract both months as YYYY-MM.
- For other questions, use unknown only if unrelated to sales.

Question: {question}
"""

    # Ask the local LLM to return structured JSON
    response = ollama.chat(
    model="llama3.2:1b",
    messages=[
        {
            "role": "system",
            "content": (
                "Classify the user's sales question accurately. "
                "Return JSON with keys intent, month1, month2. "
                "Allowed intents: total_revenue, top_product, "
                "monthly_revenue, top_region, month_comparison, unknown. "
                "A question asking which product generated the most "
                "revenue must return top_product, not total_revenue. "
                "For month_comparison, extract both months as YYYY-MM. "
                "For other intents, set month1 and month2 to null."
            ),
        },
        {"role": "user", "content": prompt},
    ],
    format="json",
    options={"temperature": 0},
)

    print("AI RAW RESPONSE:", response["message"]["content"])

    try:
        result = json.loads(response["message"]["content"])
    except (json.JSONDecodeError, KeyError, TypeError):
        raise ValueError("The AI returned an invalid response.")

    allowed_intents = {
        "total_revenue",
        "top_product",
        "monthly_revenue",
        "top_region",
        "month_comparison",
        "unknown",
    }

    intent = result.get("intent")

    if intent not in allowed_intents:
        raise ValueError("The AI returned an unsupported intent.")

    # The model selects an operation; Python controls execution.
    if intent == "total_revenue":
        answer = get_total_revenue()

    elif intent == "top_product":
        answer = get_top_product()

    elif intent == "monthly_revenue":
        answer = get_monthly_revenue()

    elif intent == "top_region":
        answer = get_top_region()

    elif intent == "month_comparison":
        import re

        months = re.findall(
            r"\b(20\d{2})[-/](0?[1-9]|1[0-2])\b",
            question
        )

        if len(months) < 2:
            return {
                "intent": "month_comparison",
                "clarification": (
                    "Please specify two months, such as "
                    "2026-01 and 2026-02."
                )
            }

        month1 = f"{months[0][0]}-{int(months[0][1]):02d}"
        month2 = f"{months[1][0]}-{int(months[1][1]):02d}"

        answer = compare_months(month1, month2)

       

    else:
        return {
            "intent": "unknown",
            "clarification": (
                "Please ask about total revenue, top product, "
                "monthly revenue, top region, or a comparison "
                "between two months."
            ),
        }

    return {
        "intent": intent,
        "answer": answer,
        "source": "SQLite sales database",
        "interpretation_method": "Local LLM (Llama 3.2 1B)",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        result = interpret_question(request.question)

        if result is None:
            raise HTTPException(
                status_code=400,
                detail="I couldn't identify that sales question. Try asking about total revenue, top product, monthly revenue, top region, or comparing two months.",
            )

        return {
            "question": request.question,
            **result,
        }

    except HTTPException:
        raise
    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your question.",
        )
