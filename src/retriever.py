from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.metric_engine import MetricEngine


@dataclass
class RetrievalResult:
    intent: str
    summary: dict[str, Any]
    preview_table: pd.DataFrame | None = None
    chart_df: pd.DataFrame | None = None
    chart_name: str | None = None
    chart_title: str | None = None

    def serializable_payload(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "summary": self.summary,
            "preview_table": None if self.preview_table is None else self.preview_table.to_dict(orient="records"),
            "chart_name": self.chart_name,
            "chart_title": self.chart_title,
        }


class BIRetriever:
    def __init__(self, engine: MetricEngine):
        self.engine = engine

    def retrieve(self, user_query: str, conversation_context: list[dict[str, str]] | None = None) -> RetrievalResult:
        q = user_query.lower()
        context_text = " ".join(item.get("user_query", "") for item in (conversation_context or [])[-3:]).lower()

        if any(word in q for word in ["trend", "over time", "monthly", "quarter", "year", "time period"]):
            period = "month"
            if "quarter" in q:
                period = "quarter"
            elif "year" in q:
                period = "year"
            trend = self.engine.sales_trend(period)
            best = trend.loc[trend["sales"].idxmax()]
            worst = trend.loc[trend["sales"].idxmin()]
            return RetrievalResult(
                intent=f"sales_trend_{period}",
                summary={
                    "highest_period": best["period"],
                    "highest_sales": round(float(best["sales"]), 2),
                    "lowest_period": worst["period"],
                    "lowest_sales": round(float(worst["sales"]), 2),
                },
                preview_table=trend,
                chart_df=trend,
                chart_name="line_sales_trend",
                chart_title=f"Sales Trend by {period.title()}",
            )

        if "region" in q or ("underperform" in q and "product" not in q):
            regional = self.engine.regional_performance()
            top_region = regional.iloc[0]
            bottom_region = regional.iloc[-1]
            return RetrievalResult(
                intent="regional_analysis",
                summary={
                    "top_region": top_region["Region"],
                    "top_region_sales": round(float(top_region["total_sales"]), 2),
                    "bottom_region": bottom_region["Region"],
                    "bottom_region_sales": round(float(bottom_region["total_sales"]), 2),
                },
                preview_table=regional,
                chart_df=regional[["Region", "total_sales"]],
                chart_name="bar_region_sales",
                chart_title="Regional Sales Analysis",
            )

        if "product" in q:
            product = self.engine.product_performance()
            top_product = product.iloc[0]
            bottom_product = product.iloc[-1]
            return RetrievalResult(
                intent="product_analysis",
                summary={
                    "top_product": top_product["Product"],
                    "top_product_sales": round(float(top_product["total_sales"]), 2),
                    "bottom_product": bottom_product["Product"],
                    "bottom_product_sales": round(float(bottom_product["total_sales"]), 2),
                },
                preview_table=product,
                chart_df=product[["Product", "total_sales"]],
                chart_name="bar_product_sales",
                chart_title="Product Performance",
            )

        if "gender" in q:
            gender = self.engine.gender_segmentation()
            top_gender = gender.iloc[0]
            return RetrievalResult(
                intent="gender_segmentation",
                summary={
                    "top_gender": top_gender["Customer_Gender"],
                    "top_gender_sales": round(float(top_gender["total_sales"]), 2),
                },
                preview_table=gender,
                chart_df=gender[["Customer_Gender", "total_sales"]],
                chart_name="bar_gender_sales",
                chart_title="Sales by Gender",
            )

        if "age" in q or "demographic" in q or "segment" in q or "segmentation" in q:
            age = self.engine.age_segmentation()
            top_group = age.iloc[0]
            return RetrievalResult(
                intent="age_segmentation",
                summary={
                    "top_age_group": str(top_group["Age_Group"]),
                    "top_age_group_sales": round(float(top_group["total_sales"]), 2),
                },
                preview_table=age,
                chart_df=age[["Age_Group", "total_sales"]].assign(Age_Group=lambda d: d["Age_Group"].astype(str)),
                chart_name="bar_age_sales",
                chart_title="Customer Segmentation by Age Group",
            )

        if "satisfaction" in q:
            if "region" in q or "regional" in q:
                sat = self.engine.satisfaction_by_region()
                top = sat.iloc[0]
                return RetrievalResult(
                    intent="satisfaction_by_region",
                    summary={
                        "top_region": top["Region"],
                        "top_satisfaction": round(float(top["avg_satisfaction"]), 2),
                    },
                    preview_table=sat,
                    chart_df=sat,
                    chart_name="bar_region_satisfaction",
                    chart_title="Average Satisfaction by Region",
                )
            sat = self.engine.satisfaction_by_product()
            top = sat.iloc[0]
            return RetrievalResult(
                intent="satisfaction_by_product",
                summary={
                    "top_product": top["Product"],
                    "top_satisfaction": round(float(top["avg_satisfaction"]), 2),
                },
                preview_table=sat,
                chart_df=sat,
                chart_name="bar_product_satisfaction",
                chart_title="Average Satisfaction by Product",
            )

        if any(word in q for word in ["median", "standard deviation", "std", "average", "summary", "overall", "kpi"]):
            summary = self.engine.summary_stats()
            preview = pd.DataFrame([summary])
            return RetrievalResult(
                intent="summary_stats",
                summary=summary,
                preview_table=preview,
            )

        if "follow up" in q or ("that" in q and "region" in context_text):
            regional = self.engine.regional_performance()
            return RetrievalResult(
                intent="regional_analysis",
                summary={"hint": "Context fallback to regional analysis"},
                preview_table=regional,
                chart_df=regional[["Region", "total_sales"]],
                chart_name="bar_region_sales",
                chart_title="Regional Sales Analysis",
            )

        summary = self.engine.summary_stats()
        preview = pd.DataFrame([summary])
        return RetrievalResult(
            intent="summary_stats",
            summary=summary,
            preview_table=preview,
        )
