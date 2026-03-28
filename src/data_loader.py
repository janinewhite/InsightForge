from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Region",
    "Sales",
    "Customer_Age",
    "Customer_Gender",
    "Customer_Satisfaction",
]


def load_dataset(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type. Use CSV or XLSX.")

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Customer_Age"] = pd.to_numeric(df["Customer_Age"], errors="coerce")
    df["Customer_Satisfaction"] = pd.to_numeric(df["Customer_Satisfaction"], errors="coerce")

    df = df.dropna(subset=["Date", "Sales", "Customer_Age", "Customer_Satisfaction"]).copy()

    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.to_period("M").astype(str)
    df["quarter"] = df["Date"].dt.to_period("Q").astype(str)
    df["weekday"] = df["Date"].dt.day_name()

    df["Age_Group"] = pd.cut(
        df["Customer_Age"],
        bins=[0, 25, 40, 60, 120],
        labels=["18-25", "26-40", "41-60", "60+"],
        include_lowest=True,
    )

    return df
