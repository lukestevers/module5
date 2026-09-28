"""src/datafun/app.py - Project script.

Author: Denise Case
Date: 2026-08

HOW TO RUN THIS FILE:

From the VS Code menu (with only this project open in VS Code),
click "Terminal" / New Terminal to
open an integrated Terminal in the root project folder.
Paste the following command and press ENTER or RETURN
to run this file as a script:

uv run python -m datafun.app

DOMAIN:

A small business with regions, stores, and employees.

The data is stored in three related CSV files:

- one row per region
- one row per store
- one row per employee

One region can have many stores.
One store can have many employees.

EXPLORE:

Sometimes the information needed for an analysis
is stored in more than one related table.

SQL is especially useful when tables share keys
and we want to analyze information across them.

A simple Python and SQL process is:

1. LOAD the related tables.
2. INSPECT the grain and keys.
3. CREATE a SQLite database.
4. LOAD the tables into SQLite.
5. QUERY across related tables with SQL.
6. VISUALIZE the query result with Python.
7. SUMMARIZE what you found.
8. DISPLAY the visualization.

DESIGN:

Use this file to declare the data-specific choices
and the reasoning behind them,
then orchestrate the work.

SQLite comes from the Python Standard Library.
Pandas loads tabular data into SQLite
and returns SQL query results as DataFrames.
Reusable visualization functions come from eda-vizkit.

The SQL stays here because the query is an
analytical decision specific to this project.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import logging
from pathlib import Path
import sqlite3
from typing import Final

from datafun_toolkit.logger import get_logger, log_header, log_path
from eda_vizkit import save_chart
import matplotlib.pyplot as plt
import pandas as pd

# === CONFIGURE LOGGER ONCE FOR THE APPLICATION ===

LOG: logging.Logger = get_logger("P05", level="DEBUG")

# === DECLARE GLOBAL CONSTANTS ===

# Some global variables are CONSTANT.
# They do NOT change while the program runs.
# By convention, constants use UPPERCASE_WITH_UNDERSCORES.
# Final indicates that the value should not be reassigned.

# === LOCATE THE DATA FILES ===

DATA_DIR: Final[Path] = Path("data") / "retail"

STORE_FILE: Final[Path] = DATA_DIR / "store.csv"
SALE_FILE: Final[Path] = DATA_DIR / "sale.csv"

# === LOCATE THE SQLITE DATABASE ===

DATABASE_FILE: Final[Path] = DATA_DIR / "business.sqlite"

# === LOCATE THE CHART OUTPUT ===

CHART_DIR: Final[Path] = Path("docs") / "images"
CHART_PATH: Final[Path] = CHART_DIR / "first-chart.png"

# === DETERMINE WHAT ONE ROW REPRESENTS ===

STORE_GRAIN: Final[str] = "one store"
SALE_GRAIN: Final[str] = "one sale transaction"

# === DESCRIBE THE TABLE RELATIONSHIPS ===

RELATIONSHIP_DECISION: Final[str] = r"""
The data is stored in two related tables.

One store can have many sales.

The sales table uses store_id to identify
the store associated with each transaction.

The shared store_id key connects store information
to sales information.
"""

# === DEFINE THE ANALYTICAL QUESTION ===

CUSTOM_QUERY_DECISION: Final[str] = r"""
I want to compare purchasing patterns between
cash and non-cash transactions.

The result should show each product group
and compare the number of transactions
and items sold for each payment category.

The information requires both tables:
 - store information is in stores,
 - sales and payment information is in sales.

The tables are connected through store_id.
"""

# === WRITE THE SQL QUERY ===

CUSTOM_SQL_QUERY: Final[str] = """
SELECT
    s.store_name,
    sa.product_group,
    CASE
        WHEN sa.payment_type = 'Cash' THEN 'Cash'
        ELSE 'Non-Cash'
    END AS payment_category,
    COUNT(sa.sale_id) AS transaction_count,
    SUM(sa.items_sold) AS items_sold,
    SUM(sa.sale_amount) AS total_sales
FROM stores AS s
JOIN sales AS sa
    ON s.store_id = sa.store_id
GROUP BY
    s.store_name,
    sa.product_group,
    payment_category
ORDER BY
    s.store_name,
    sa.product_group,
    payment_category;
"""

# === CHOOSE A VISUALIZATION ===

CUSTOM_CHART_DECISION: Final[str] = r"""
The query result compares purchases
by product group and payment category.

A grouped bar chart can show differences
between cash and non-cash purchases
across product groups.
"""


# === DEFINE THE MAIN FUNCTION ===


def main() -> None:
    """Entry point when running this file as a Python script.

    This is where the instructions begin.

    Arguments: None.
    Returns: None.
    """
    log_header(LOG, "P05 - PYTHON AND SQL")

    LOG.info("===================================")
    LOG.info("START main()")
    LOG.info("===================================")

    LOG.info("-------------------------------")
    LOG.info("01. LOAD the related tables.")
    LOG.info("-------------------------------")

    log_path(LOG, "stores file", path=STORE_FILE)
    log_path(LOG, "sales file", path=SALE_FILE)

    stores_df: pd.DataFrame = pd.read_csv(STORE_FILE)
    sales_df: pd.DataFrame = pd.read_csv(SALE_FILE)

    LOG.info("Related tables loaded successfully.")

    LOG.info("-------------------------------")
    LOG.info("02. INSPECT the grain and keys.")
    LOG.info("-------------------------------")

    LOG.info(f"Stores grain: {STORE_GRAIN}")
    LOG.info(f"Sales grain: {SALE_GRAIN}")

    LOG.info(f"Stores columns: {stores_df.columns.tolist()}")
    LOG.info(f"Sales columns: {sales_df.columns.tolist()}")

    LOG.info(RELATIONSHIP_DECISION)

    LOG.info("-------------------------------")
    LOG.info("03. CREATE a SQLite database.")
    LOG.info("-------------------------------")

    log_path(LOG, "SQLite database", path=DATABASE_FILE)

    connection: sqlite3.Connection = sqlite3.connect(DATABASE_FILE)

    LOG.info("SQLite database connection created.")

    LOG.info("-------------------------------")
    LOG.info("04. LOAD the tables into SQLite.")
    LOG.info("-------------------------------")

    stores_df.to_sql(
        "stores",
        connection,
        if_exists="replace",
        index=False,
    )

    sales_df.to_sql(
        "sales",
        connection,
        if_exists="replace",
        index=False,
    )

    LOG.info("Related tables loaded into SQLite.")

    LOG.info("-------------------------------")
    LOG.info("05. QUERY across related tables with SQL.")
    LOG.info("-------------------------------")

    LOG.info(CUSTOM_QUERY_DECISION)
    LOG.info(f"\nSQL query:\n{CUSTOM_SQL_QUERY}")

    result_df: pd.DataFrame = pd.read_sql_query(
        CUSTOM_SQL_QUERY,
        connection,
    )

    LOG.info(f"\nQuery result:\n{result_df}")

    LOG.info("-------------------------------")
    LOG.info("06. VISUALIZE the query result with Python.")
    LOG.info("-------------------------------")

    LOG.info(CUSTOM_CHART_DECISION)

    purchase_ax = (
        result_df.groupby(["product_group", "payment_category"])["items_sold"]
        .sum()
        .unstack()
        .plot.bar()
    )

    purchase_ax.set_title("Items Sold by Product Group and Payment Type")
    purchase_ax.set_xlabel("Product Group")
    purchase_ax.set_ylabel("Items Sold")
    purchase_ax.legend(title="Payment Category")

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    save_chart(
        purchase_ax,
        CHART_PATH,
    )

    LOG.info(f"Chart saved successfully at {CHART_PATH}.")

    LOG.info("-------------------------------")
    LOG.info("07. SUMMARIZE what you found.")
    LOG.info("-------------------------------")

    # Run this app first.
    # Review the SQL result and visualization.
    # Then record your CUSTOM observations
    # in a simple multi-line raw string.

    LOG.info(
        r"""CUSTOM OBSERVATIONS:
The SQL query connected the stores and sales tables
using the shared store_id key.

The result compares product groups by
cash and non-cash payment categories.

I observed that non-cash purchases were higher than cash purchases
in every product group. Grocery had the most items sold overall,
with 50 cash items and 103 non-cash items. Outdoor showed one
of the largest differences, with 19 cash items compared with
70 non-cash items.

Based on this result, I would next like to explore whether
non-cash transactions also have higher average sale amounts
than cash transactions.
"""
    )

    LOG.info("-------------------------------")
    LOG.info("08. DISPLAY the visualization.")
    LOG.info("-------------------------------")

    LOG.info("In a script, call plt.show() at the end to display all charts.")
    LOG.info("Close all chart windows (with the close button) to continue.")

    plt.show()

    connection.close()

    LOG.info("===================================")
    LOG.info("END main() - Executed successfully!")
    LOG.info("===================================")


# === CONDITIONAL EXECUTION GUARD ===

# WHY: This is standard Python "boilerplate" - we copy and paste it
# into every Python script. It is a "conditional execution" guard,
# meaning: if this file is being run as a script, then execute the code
# in the main() function.

if __name__ == "__main__":
    main()
