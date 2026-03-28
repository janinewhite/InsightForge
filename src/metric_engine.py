from __future__ import annotations

import pandas as pd


class MetricEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def summary_stats(self) -> dict[str, float]:
        sales = self.df["Sales"]
        return {
            "total_sales": float(sales.sum()),
            "average_sales": float(sales.mean()),
            "median_sales": float(sales.median()),
            "std_sales": float(sales.std(ddof=1)),
            "min_sales": float(sales.min()),
            "max_sales": float(sales.max()),
            "transactions": float(len(self.df)),
        }

    def sales_trend(self, period: str = "month") -> pd.DataFrame:
        if period not in {"month", "quarter", "year", "weekday"}:
            raise ValueError("Unsupported period.")
        return (
            self.df.groupby(period, as_index=False)["Sales"]
            .sum()
            .sort_values(period)
            .rename(columns={period: "period", "Sales": "sales"})
        )

    def product_performance(self) -> pd.DataFrame:
        return (
            self.df.groupby("Product", as_index=False)
            .agg(
                total_sales=("Sales", "sum"),
                average_sales=("Sales", "mean"),
                avg_satisfaction=("Customer_Satisfaction", "mean"),
            )
            .sort_values("total_sales", ascending=False)
        )

    def regional_performance(self) -> pd.DataFrame:
        return (
            self.df.groupby("Region", as_index=False)
            .agg(
                total_sales=("Sales", "sum"),
                average_sales=("Sales", "mean"),
                avg_satisfaction=("Customer_Satisfaction", "mean"),
            )
            .sort_values("total_sales", ascending=False)
        )

    def age_segmentation(self) -> pd.DataFrame:
        return (
            self.df.groupby("Age_Group", as_index=False, observed=False)
            .agg(
                total_sales=("Sales", "sum"),
                average_sales=("Sales", "mean"),
                avg_satisfaction=("Customer_Satisfaction", "mean"),
            )
            .sort_values("total_sales", ascending=False)
        )

    def gender_segmentation(self) -> pd.DataFrame:
        return (
            self.df.groupby("Customer_Gender", as_index=False)
            .agg(
                total_sales=("Sales", "sum"),
                average_sales=("Sales", "mean"),
                avg_satisfaction=("Customer_Satisfaction", "mean"),
            )
            .sort_values("total_sales", ascending=False)
        )

    def satisfaction_by_product(self) -> pd.DataFrame:
        return (
            self.df.groupby("Product", as_index=False)["Customer_Satisfaction"]
            .mean()
            .rename(columns={"Customer_Satisfaction": "avg_satisfaction"})
            .sort_values("avg_satisfaction", ascending=False)
        )

    def satisfaction_by_region(self) -> pd.DataFrame:
        return (
            self.df.groupby("Region", as_index=False)["Customer_Satisfaction"]
            .mean()
            .rename(columns={"Customer_Satisfaction": "avg_satisfaction"})
            .sort_values("avg_satisfaction", ascending=False)
        )
