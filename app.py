from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.agent import InsightAgent
from src.charts import build_chart
from src.config import AppConfig
from src.data_loader import load_dataset
from src.logger import AppLogger
from src.memory import ConversationMemory
from src.metric_engine import MetricEngine
from src.retriever import BIRetriever


st.set_page_config(page_title="InsightForge", layout="wide")


@st.cache_data(show_spinner=False)
def get_dataframe_from_path(path: str) -> pd.DataFrame:
    return load_dataset(path)


def render_dataset_overview(df: pd.DataFrame, engine: MetricEngine) -> None:
    summary = engine.summary_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"${summary['total_sales']:,.0f}")
    c2.metric("Average Sale", f"${summary['average_sales']:,.2f}")
    c3.metric("Median Sale", f"${summary['median_sales']:,.2f}")
    c4.metric("Std Dev", f"${summary['std_sales']:,.2f}")

    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(20), use_container_width=True)


def main() -> None:
    config = AppConfig.from_env()
    logger = AppLogger(config.db_path)
    st.title("InsightForge")
    st.caption("AI-powered business intelligence assistant for structured sales analytics")

    uploaded = st.sidebar.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])
    use_sample = st.sidebar.checkbox("Use bundled sample sales data", value=uploaded is None)

    if uploaded is not None:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        uploaded_path = data_dir / uploaded.name
        uploaded_path.write_bytes(uploaded.getbuffer())
        df = load_dataset(str(uploaded_path))
        dataset_name = uploaded.name
    elif use_sample:
        df = get_dataframe_from_path(str(config.default_data_path))
        dataset_name = config.default_data_path.name
    else:
        st.info("Upload a CSV/XLSX file or enable the sample dataset.")
        return

    engine = MetricEngine(df)
    retriever = BIRetriever(engine)
    memory = ConversationMemory(st.session_state)
    agent = InsightAgent(config=config)

    render_dataset_overview(df, engine)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Dataset loaded. Ask about trends, products, regions, demographics, satisfaction, or summary statistics."
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart_spec"):
                chart_data = pd.DataFrame(message["chart_spec"]["data"])
                fig = build_chart(
                    chart_name=message["chart_spec"]["chart_name"],
                    chart_df=chart_data,
                    title=message["chart_spec"]["title"],
                )
                st.plotly_chart(fig, use_container_width=True)
            if message.get("table_data"):
                st.dataframe(pd.DataFrame(message["table_data"]), use_container_width=True)

    user_query = st.chat_input("Ask a business question")
    if not user_query:
        return

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    retrieval = retriever.retrieve(user_query, memory.context())
    answer = agent.answer(
        user_query=user_query,
        retrieval=retrieval,
        conversation_context=memory.context(),
    )

    assistant_message = {
        "role": "assistant",
        "content": answer["text"],
        "table_data": retrieval.preview_table.to_dict(orient="records") if retrieval.preview_table is not None else None,
        "chart_spec": None,
    }

    if retrieval.chart_df is not None and retrieval.chart_name:
        assistant_message["chart_spec"] = {
            "chart_name": retrieval.chart_name,
            "title": retrieval.chart_title,
            "data": retrieval.chart_df.to_dict(orient="records"),
        }

    st.session_state.messages.append(assistant_message)
    memory.remember(user_query=user_query, answer_text=answer["text"], retrieval_intent=retrieval.intent)

    with st.chat_message("assistant"):
        st.markdown(answer["text"])
        if retrieval.chart_df is not None and retrieval.chart_name:
            fig = build_chart(
                chart_name=retrieval.chart_name,
                chart_df=retrieval.chart_df,
                title=retrieval.chart_title,
            )
            st.plotly_chart(fig, use_container_width=True)
        if retrieval.preview_table is not None:
            st.dataframe(retrieval.preview_table, use_container_width=True)

    logger.log_interaction(
        dataset_name=dataset_name,
        user_query=user_query,
        retrieval_intent=retrieval.intent,
        retrieval_payload=json.dumps(retrieval.serializable_payload(), default=str),
        answer_text=answer["text"],
        used_llm=answer["used_llm"],
    )

    with st.sidebar.expander("Conversation memory", expanded=False):
        st.json(memory.context())


if __name__ == "__main__":
    main()
