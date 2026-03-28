from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from src.config import AppConfig
from src.prompts import SYSTEM_PROMPT
from src.retriever import RetrievalResult


class InsightAgent:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key) if config.openai_api_key else None

    def answer(
        self,
        user_query: str,
        retrieval: RetrievalResult,
        conversation_context: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if self.client is not None:
            try:
                text = self._llm_answer(user_query, retrieval, conversation_context or [])
                return {"text": text, "used_llm": True}
            except Exception:
                pass

        return {"text": self._fallback_answer(user_query, retrieval), "used_llm": False}

    def _llm_answer(
        self,
        user_query: str,
        retrieval: RetrievalResult,
        conversation_context: list[dict[str, str]],
    ) -> str:
        prompt_text = (
            f"User question: {user_query}\n\n"
            f"Conversation context: {json.dumps(conversation_context[-5:], default=str)}\n\n"
            f"Retrieved intent: {retrieval.intent}\n"
            f"Retrieved summary: {json.dumps(retrieval.summary, default=str)}\n"
            f"Retrieved table sample: {json.dumps(retrieval.serializable_payload(), default=str)}"
        )

        response = self.client.responses.create(
            model=self.config.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text},
            ],
        )
        return response.output_text.strip()

    def _fallback_answer(self, user_query: str, retrieval: RetrievalResult) -> str:
        intent = retrieval.intent
        s = retrieval.summary

        if intent.startswith("sales_trend"):
            return (
                f"The strongest period in the retrieved trend is {s['highest_period']} with sales of "
                f"${s['highest_sales']:,.2f}, while the weakest period is {s['lowest_period']} at "
                f"${s['lowest_sales']:,.2f}. This indicates a meaningful swing over time. "
                f"Use the peaks to identify what campaigns, inventory mix, or seasonality drove performance, "
                f"and investigate the weaker periods for pricing, promotion, or demand issues."
            )

        if intent == "regional_analysis":
            return (
                f"{s['top_region']} is the top-performing region with ${s['top_region_sales']:,.2f} in sales, "
                f"while {s['bottom_region']} is the weakest at ${s['bottom_region_sales']:,.2f}. "
                f"Prioritize a diagnostic review of the weaker region's product mix, channel coverage, and local promotions. "
                f"Replicating tactics from the leading region is the fastest starting point."
            )

        if intent == "product_analysis":
            return (
                f"{s['top_product']} leads product revenue at ${s['top_product_sales']:,.2f}, while "
                f"{s['bottom_product']} trails at ${s['bottom_product_sales']:,.2f}. "
                f"That suggests your assortment is not contributing evenly. Consider protecting inventory and marketing support "
                f"for the strongest product while reviewing pricing, positioning, or bundling for the weakest one."
            )

        if intent == "gender_segmentation":
            return (
                f"The highest total sales come from the {s['top_gender']} segment at "
                f"${s['top_gender_sales']:,.2f}. Use this as a signal for message resonance and channel performance, "
                f"but avoid overfitting strategy to one segment alone. Compare conversion and satisfaction before reallocating spend."
            )

        if intent == "age_segmentation":
            return (
                f"The leading age segment is {s['top_age_group']} with total sales of "
                f"${s['top_age_group_sales']:,.2f}. This segment is currently the most commercially valuable in the dataset. "
                f"Targeted creative, tailored offers, and retention campaigns for this age band are likely to produce the best near-term return."
            )

        if intent == "satisfaction_by_product":
            return (
                f"{s['top_product']} has the highest average customer satisfaction at {s['top_satisfaction']:.2f}. "
                f"This is a useful quality signal. Consider whether the attributes driving this satisfaction can be translated to lower-performing products."
            )

        if intent == "satisfaction_by_region":
            return (
                f"{s['top_region']} has the highest average customer satisfaction at {s['top_satisfaction']:.2f}. "
                f"This suggests a stronger customer experience in that market. Compare service, fulfillment, and product availability there against other regions."
            )

        if intent == "summary_stats":
            return (
                f"Overall sales total ${s['total_sales']:,.2f}, with an average sale of ${s['average_sales']:,.2f}, "
                f"a median sale of ${s['median_sales']:,.2f}, and a standard deviation of ${s['std_sales']:,.2f}. "
                f"The gap between mean and variability suggests you should evaluate whether a small set of larger orders is driving performance."
            )

        return "The requested analysis ran successfully, but I could not generate a more specific narrative for that intent."