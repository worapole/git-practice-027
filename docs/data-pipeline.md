# Sales Data Pipeline (Silver → Gold)

This repository contains a 3-step Databricks/PySpark notebook flow that builds a sales pipeline from source tables into Silver and Gold Delta tables.

## Purpose and flow

- Build a curated **Silver** sales table by joining transaction, customer, and franchise data.
- Build a **Gold daily KPI** table aggregated by sales date.
- A third notebook is present for sentiment summary, but it is **not currently producing a sentiment table**.

```mermaid
flowchart TD
  A[samples.bakehouse.sales_transactions]
  B[samples.bakehouse.sales_customers]
  C[samples.bakehouse.sales_franchises]
  D[ctl_training_dev.m3.silver_sales]
  E[ctl_training_dev.m3.gold_sales_daily]
  F[ctl_training_dev.m3.gold_sentiment_summary<br/>(not currently written)]

  A --> D
  B --> D
  C --> D
  D --> E
  E -. read only .-> F
```

## Notebook-by-notebook details

### 1) `src/1_silver_sales.ipynb`

**Sources**
- `samples.bakehouse.sales_transactions`
- `samples.bakehouse.sales_customers`
- `samples.bakehouse.sales_franchises`

**Key transformations**
- Drops `city` and `country` from customers.
- Left-joins:
  - transactions ↔ customers on `customerID`
  - result ↔ franchises on `franchiseID`
- Removes duplicates by `transactionID` (`dropDuplicates(["transactionID"])`).

**Target**
- Writes Delta table (overwrite mode): `ctl_training_dev.m3.silver_sales`

---

### 2) `src/2_gold_sales_daily.ipynb`

**Source**
- `ctl_training_dev.m3.silver_sales`

**Key transformations**
- Derives `sales_date` from `dateTime` using `to_date`.
- Aggregates by `sales_date`:
  - `revenue` = `sum(totalPrice)`
  - `transactions` = `countDistinct(transactionID)`
  - `customers` = `countDistinct(customerID)`

**Target**
- Writes Delta table (overwrite mode): `ctl_training_dev.m3.gold_sales_daily`

---

### 3) `src/3_gold_sentiment_summary.ipynb` (current status)

**Current actual behavior**
- Reads `ctl_training_dev.m3.gold_sales_daily` into `reviews`.
- Sentiment transformation, aggregation, and write to `ctl_training_dev.m3.gold_sentiment_summary` are all commented out.
- The notebook still prints `gold_sentiment_summary created`, which is misleading because no table write occurs.

**Current limitation**
- The commented sentiment logic expects a `rating` column.
- `ctl_training_dev.m3.gold_sales_daily` is built from daily KPIs (`sales_date`, `revenue`, `transactions`, `customers`) and does not provide `rating`.
- Because of this schema mismatch, the commented sentiment logic is not aligned with the current source table.

## Execution order and dependencies

Run notebooks in this order:
1. `src/1_silver_sales.ipynb`
2. `src/2_gold_sales_daily.ipynb`
3. `src/3_gold_sentiment_summary.ipynb` (currently read/print only; no output table write)

Dependency chain:
- Notebook 2 depends on Notebook 1 output (`silver_sales`).
- Notebook 3 currently depends on Notebook 2 output (`gold_sales_daily`) but does not materialize sentiment output.

## Operational notes

- Writes use `.mode("overwrite")` for target Delta tables.
- Requires Databricks/Spark runtime and access to referenced catalogs/schemas/tables:
  - `samples.bakehouse.*`
  - `ctl_training_dev.m3.*`
