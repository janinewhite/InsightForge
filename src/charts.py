from __future__ import annotations

import plotly.express as px
import pandas as pd


def build_chart(chart_name: str, chart_df: pd.DataFrame, title: str):
    if chart_name == "line_sales_trend":
        return px.line(chart_df, x="period", y="sales", markers=True, title=title)
    if chart_name == "bar_product_sales":
        return px.bar(chart_df, x="Product", y="total_sales", title=title)
    if chart_name == "bar_region_sales":
        return px.bar(chart_df, x="Region", y="total_sales", title=title)
    if chart_name == "bar_gender_sales":
        return px.bar(chart_df, x="Customer_Gender", y="total_sales", title=title)
    if chart_name == "bar_age_sales":
        return px.bar(chart_df, x="Age_Group", y="total_sales", title=title)
    if chart_name == "bar_product_satisfaction":
        return px.bar(chart_df, x="Product", y="avg_satisfaction", title=title)
    if chart_name == "bar_region_satisfaction":
        return px.bar(chart_df, x="Region", y="avg_satisfaction", title=title)
    raise ValueError(f"Unsupported chart type: {chart_name}")
