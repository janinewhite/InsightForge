from __future__ import annotations

import json
from typing import Any

from src.config import AppConfig
from src.data_loader import load_dataset
from src.metric_engine import MetricEngine
from src.retriever import BIRetriever
from src.agent import InsightAgent


TEST_CASES = [
    {
        "question": "Which region performs best?",
        "expected_keyword": "region",
    },
    {
        "question": "Show sales trend over time",
        "expected_keyword": "period",
    },
    {
        "question": "What is the median sales?",
        "expected_keyword": "median",
    },
]


def run_evaluation() -> list[dict[str, Any]]:
    config = AppConfig()
    df = load_dataset("data/sales_data.csv")

    engine = MetricEngine(df)
    retriever = BIRetriever(engine)
    agent = InsightAgent(config)

    results = []

    print("Running evaluation...\n")

    for case in TEST_CASES:
        question = case["question"]

        retrieval = retriever.retrieve(question)
        response = agent.answer(question, retrieval)

        result = {
            "question": question,
            "intent": retrieval.intent,
            "answer": response["text"],
        }

        print(f"Question: {question}")
        print(f"Intent: {retrieval.intent}")
        print(f"Answer: {response['text'][:120]}...\n")

        results.append(result)

    return results


if __name__ == "__main__":
    results = run_evaluation()

    print("Evaluation complete.\n")

    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Results saved to evaluation_results.json")