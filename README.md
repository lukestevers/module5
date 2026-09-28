# datafun-05-sql

[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![uv managed](https://img.shields.io/badge/uv-managed-DE5FE9)](https://docs.astral.sh/uv/)
[![SQLite](https://img.shields.io/badge/SQLite-database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![marimo](https://img.shields.io/badge/marimo-reactive_notebook-FF6B6B)](https://docs.marimo.io/)
[![Zensical docs](https://img.shields.io/badge/Zensical-docs-purple)](https://zensical.org/)
[![MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

> A Python and SQL analytics project exploring purchasing patterns in retail sales.

## Project Overview

This project demonstrates how Python and SQL can be combined to analyze related business data.

For my custom analysis, I focused on **retail sales transactions** and compared purchasing patterns between **cash and non-cash payments**.

The analysis uses two related tables:

- `stores` — one row per store
- `sales` — one row per sale transaction

The tables are connected through the shared `store_id` key.

The project loads the CSV data into SQLite, uses SQL to join and summarize the related tables, returns the query results to a Pandas DataFrame, and uses Python to create a visualization.

## Custom Analysis Question

> **How do purchasing patterns differ between cash and non-cash transactions, and which product groups are purchased most often by each payment category?**

For this analysis:

- `Cash` transactions remain in the **Cash** category.
- `Card` and `Mobile` transactions are grouped into **Non-Cash**.
- Purchases are compared by product group.
- The analysis considers transaction counts, items sold, and sales amounts.

## SQL Analysis

The project uses a SQL `JOIN` to connect store information with sales:

```sql
FROM stores AS s
JOIN sales AS sa
    ON s.store_id = sa.store_id
