
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"


def load_sales_data():
    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV file found in the data folder."
        )

    # Load the supplied CSV
    df = pd.read_csv(csv_files[0])

    # Validate required columns
    required_columns = [
        "Transaction_Id",
        "Order_date",
        "Product",
        "Category",
        "Region",
        "Sales_channel",
        "Quantity",
        "Unit_price",
        "Discount_amount",
        "Status",
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Clean text fields
    text_columns = [
        "Transaction_Id",
        "Product",
        "Category",
        "Region",
        "Sales_channel",
        "Status",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Convert dates and numeric fields safely
    df["Order_date"] = pd.to_datetime(
        df["Order_date"], dayfirst=True, errors="coerce"
    )

    numeric_columns = [
        "Quantity",
        "Unit_price",
        "Discount_amount",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Identify data-quality issues without guessing missing prices
    df["Data_quality_issue"] = ""

    missing_price = df["Unit_price"].isna()
    df.loc[missing_price, "Data_quality_issue"] = (
        "Missing unit price"
    )

    invalid_date = df["Order_date"].isna()
    df.loc[invalid_date, "Data_quality_issue"] = (
        df.loc[invalid_date, "Data_quality_issue"]
        .apply(lambda x: f"{x}; " if x else "")
        + "Invalid order date"
    )

    invalid_quantity = df["Quantity"].isna() | (df["Quantity"] < 0)
    df.loc[invalid_quantity, "Data_quality_issue"] = (
        df.loc[invalid_quantity, "Data_quality_issue"]
        .apply(lambda x: f"{x}; " if x else "")
        + "Invalid quantity"
    )

    invalid_price = df["Unit_price"].notna() & (df["Unit_price"] < 0)
    df.loc[invalid_price, "Data_quality_issue"] = (
        df.loc[invalid_price, "Data_quality_issue"]
        .apply(lambda x: f"{x}; " if x else "")
        + "Negative unit price"
    )

    invalid_discount = (
        df["Discount_amount"].isna()
        | (df["Discount_amount"] < 0)
    )
    df.loc[invalid_discount, "Data_quality_issue"] = (
        df.loc[invalid_discount, "Data_quality_issue"]
        .apply(lambda x: f"{x}; " if x else "")
        + "Invalid discount"
    )

    # Calculate revenue only when the record is eligible and complete
    valid_revenue = (
        df["Status"].str.casefold().eq("completed")
        & df["Unit_price"].notna()
        & df["Order_date"].notna()
        & df["Quantity"].notna()
        & (df["Quantity"] > 0)
        & (df["Unit_price"] >= 0)
        & df["Discount_amount"].notna()
        & (df["Discount_amount"] >= 0)
    )

    df["Revenue"] = pd.NA
    df.loc[valid_revenue, "Revenue"] = (
        df.loc[valid_revenue, "Quantity"]
        * df.loc[valid_revenue, "Unit_price"]
        - df.loc[valid_revenue, "Discount_amount"]
    )

    # Preserve every input row in SQLite for auditability
    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql(
            "sales",
            connection,
            if_exists="replace",
            index=False,
        )

    return df


if __name__ == "__main__":
    sales = load_sales_data()

    print("Database created:", DB_PATH)
    print("Rows loaded:", len(sales))
    print("Rows with data-quality issues:",
          (sales["Data_quality_issue"] != "").sum())
    print("Rows eligible for revenue:", sales["Revenue"].notna().sum())
    print("Total eligible revenue:",
          sales["Revenue"].sum(skipna=True))
    print("\nData-quality issues:")
    print(
        sales.loc[
            sales["Data_quality_issue"] != "",
            ["Transaction_Id", "Status", "Quantity",
             "Unit_price", "Data_quality_issue"]
        ].to_string(index=False)
    )

    print("\nCompleted rows excluded from revenue:")
    excluded = sales[
        sales["Status"].str.casefold().eq("completed")
        & sales["Revenue"].isna()
    ]

    print(
        excluded[
            [
                "Transaction_Id",
                "Quantity",
                "Unit_price",
                "Discount_amount",
                "Data_quality_issue",
            ]
        ].to_string(index=False)
    )
