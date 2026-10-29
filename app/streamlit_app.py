
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI Sales Intelligence Assistant",
    page_icon="📊",
    layout="centered"
)

st.title("📊 AI Sales Intelligence Assistant")
st.write(
    "Ask questions about sales data and get "
    "answers backed by our SQLite database."
)

st.subheader("Ask a business question")

question = st.text_input(
    "Your question",
    placeholder="Which product generated the most revenue?"
)

examples = [
    "What is the total revenue?",
    "Which product generated the most revenue?",
    "Show monthly revenue",
    "Which region has the highest sales?",
    "Compare revenue between 2026-01 and 2026-02"
]

st.caption("Example questions")
for example in examples:
    st.write(f"• {example}")

if st.button("Get Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Analyzing your question..."):
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=60
                )

            if response.status_code == 200:
                result = response.json()

                st.success("Answer generated successfully!")
                st.write("**Your question:**", result.get("question"))
                st.write("**Detected intent:**", result.get("intent"))

                answer = result.get("answer", {})

                if isinstance(answer, dict):
                    if "total_revenue" in answer:
                        st.metric(
                            "Total Revenue",
                            f"₹{answer['total_revenue']:,.2f}"
                        )
                        st.write(
                            "Eligible transactions:",
                            answer.get("eligible_transactions", "N/A")
                        )

                    elif "Product" in answer:
                        st.metric(
                            "Top Product",
                            answer["Product"]
                        )
                        st.metric(
                            "Revenue",
                            f"₹{float(answer['Revenue']):,.2f}"
                        )

                    elif "Region" in answer:
                        st.metric("Top Region", answer["Region"])
                        if "Revenue" in answer:
                            st.metric(
                                "Revenue",
                                f"₹{float(answer['Revenue']):,.2f}"
                            )

                    elif result.get("intent") == "monthly_revenue":
                        st.subheader("Monthly Revenue")
                        df = pd.DataFrame(answer)
                        st.dataframe(df, use_container_width=True)
                        numeric_columns = df.select_dtypes(
                            include="number"
                        ).columns
                        if len(numeric_columns) > 0:
                            st.bar_chart(
                                df.set_index(df.columns[0])[numeric_columns[0]]
                            )

                    else:
                        st.json(answer)
                elif isinstance(answer, list):
                    st.dataframe(
                        pd.DataFrame(answer),
                        use_container_width=True
                    )
                else:
                    st.write(answer)

                if result.get("clarification"):
                    st.info(result["clarification"])

                st.caption(
                    "Source: SQLite sales database | "
                    "Interpretation: Local LLM"
                )
            else:
                try:
                    detail = response.json().get(
                        "detail", "Request failed."
                    )
                except ValueError:
                    detail = "Request failed."
                st.error(f"API error ({response.status_code}): {detail}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the API. "
                "Start the FastAPI server in another terminal first."
            )
        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except Exception as error:
            st.error(f"Something went wrong: {error}")
