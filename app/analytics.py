
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sales.db"


def query_database(sql, params=()):
    """Execute a read-only analytics query."""
    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row

    try:
        return [
            dict(row)
            for row in connection.execute(sql, params).fetchall()
        ]
    finally:
        connection.close()


def get_total_revenue():
    sql = """
        SELECT
            ROUND(SUM(Revenue), 2) AS total_revenue,
            COUNT(Revenue) AS eligible_transactions
        FROM sales
        WHERE Revenue IS NOT NULL
    """
    return query_database(sql)[0]


def get_top_product():
    sql = """
        SELECT
            Product,
            ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        WHERE Revenue IS NOT NULL
        GROUP BY Product
        ORDER BY revenue DESC, Product ASC
        LIMIT 1
    """
    return query_database(sql)


def get_monthly_revenue():
    sql = """
        SELECT
            strftime('%Y-%m', Order_date) AS month,
            ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        WHERE Revenue IS NOT NULL
        GROUP BY strftime('%Y-%m', Order_date)
        ORDER BY month
    """
    return query_database(sql)


def get_top_region():
    sql = """
        SELECT
            Region,
            ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        WHERE Revenue IS NOT NULL
        GROUP BY Region
        ORDER BY revenue DESC, Region ASC
        LIMIT 1
    """
    return query_database(sql)


def compare_months(month1, month2):
    """Compare two months in YYYY-MM format."""
    for month in (month1, month2):
        if (
            len(month) != 7
            or month[4] != "-"
            or not month[:4].isdigit()
            or not month[5:].isdigit()
            or not 1 <= int(month[5:]) <= 12
        ):
            raise ValueError("Months must use YYYY-MM format.")

    sql = """
        SELECT
            strftime('%Y-%m', Order_date) AS month,
            ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        WHERE Revenue IS NOT NULL
          AND strftime('%Y-%m', Order_date) IN (?, ?)
        GROUP BY strftime('%Y-%m', Order_date)
    """

    results = query_database(sql, (month1, month2))
    revenue_by_month = {
        row["month"]: row["revenue"] for row in results
    }

    first = revenue_by_month.get(month1, 0)
    second = revenue_by_month.get(month2, 0)

    return {
        "month1": month1,
        "revenue1": first,
        "month2": month2,
        "revenue2": second,
        "change": round(second - first, 2),
        "percentage_change": (
            round((second - first) / first * 100, 2)
            if first != 0 else None
        ),
    }


if __name__ == "__main__":
    print("Total revenue:", get_total_revenue())
    print("\nTop product:", get_top_product())
    print("\nMonthly revenue:", get_monthly_revenue())
    print("\nTop region:", get_top_region())
    print("\nJanuary vs February:", compare_months("2026-01", "2026-02"))
