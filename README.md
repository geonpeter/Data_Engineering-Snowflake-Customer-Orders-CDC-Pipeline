# E-Commerce Mock Data Generation and Snowflake CDC Pipeline
 This project demonstrates an end-to-end system for simulating real-time order data (CDC events) for an e-commerce platform and processing the data in Snowflake. It includes data generation, insertion, updating, and deletion, along with the creation of Snowflake tables (raw, derived, and aggregated) for reporting and analytics.
 ## Project Overview
1. Data Generation: Python script continuously generates mock order data with attributes like order_id, customer_id, order_date, status, amount, product_id, and quantity.
2. Snowflake Integration: Data is inserted, updated, and deleted in real-time into Snowflake's raw_orders table. The project uses Snowflake's dynamic tables to derive new data tables and aggregate metrics for e-commerce reporting.
3. Data Processing and Transformation:
  - Derived Table: Extracts year, month, and categories (order value and completion status) from the raw_orders table.
  - Aggregated Table: Provides monthly aggregated insights like total orders, total revenue, unique customers, average order value, and high vs. low value orders.
4. Task Automation: Snowflake tasks are used to periodically refresh the aggregated table every 2 minutes, ensuring that the reporting data is always up to date.

## Workflow Diagram
![Workflow]![image](https://github.com/user-attachments/assets/aa59f88e-619d-4ee9-b50c-080dfe0974b9)



## Directory Structure
```bash
.
├── snowflake_credentials.json      # Snowflake connection credentials
├── cdc_pipeline.py                 # Main script for generating data and interacting with Snowflake
├── README.md                       # Project documentation
└── requirements.txt                # Required Python libraries

```
## Prerequisites
- Python 3.x
- A Snowflake account
- Snowflake Python Connector (snowflake-connector-python)
- Snowflake access credentials stored in snowflake_credentials.json

## Example JSON structure:
```sql
{
  "user": "your_user",
  "password": "your_password",
  "account": "your_account",
  "warehouse": "your_warehouse",
  "database": "your_database",
  "schema": "your_schema"
}
```
## Setup and Installation
1. Clone the repository:
  ```sql
git clone https://github.com/your-repo/ecomm-cdc-snowflake.git
cd ecomm-cdc-snowflake
```
2. Install dependencies:
```sql
pip install -r requirements.txt

```
3. Snowflake Table Setup:
- In Snowflake, run the following SQL commands to set up the necessary tables:
```sql
CREATE DATABASE Ecomm;
USE Ecomm;

-- Raw orders table
CREATE OR REPLACE TABLE raw_orders (
    order_id STRING,
    customer_id STRING,
    order_date TIMESTAMP,
    status STRING,
    amount NUMBER,
    product_id STRING,
    quantity NUMBER
);

```
4. Dynamic Tables for Derived and Aggregated Data:
```sql
-- Derived table
CREATE OR REPLACE DYNAMIC TABLE orders_derived
WAREHOUSE = 'COMPUTE_WH'
TARGET_LAG = DOWNSTREAM
AS
SELECT
    order_id,
    customer_id,
    order_date,
    status,
    amount,
    product_id,
    quantity,
    EXTRACT(YEAR FROM order_date) AS order_year,
    EXTRACT(MONTH FROM order_date) AS order_month,
    CASE WHEN amount > 100 THEN 'High Value' ELSE 'Low Value' END AS order_value_category,
    CASE WHEN status = 'DELIVERED' THEN 'Completed' ELSE 'Pending' END AS order_completion_status,
    DATEDIFF('day', order_date, CURRENT_TIMESTAMP()) AS days_since_order
FROM raw_orders;

-- Aggregated table
CREATE OR REPLACE DYNAMIC TABLE orders_aggregated
WAREHOUSE = 'COMPUTE_WH'
TARGET_LAG = DOWNSTREAM
AS
SELECT
    order_year,
    order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(amount) AS total_revenue,
    AVG(amount) AS average_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS total_items_sold,
    SUM(CASE WHEN status = 'DELIVERED' THEN amount ELSE 0 END) AS total_delivered_revenue,
    SUM(CASE WHEN order_value_category = 'High Value' THEN amount ELSE 0 END) AS total_high_value_orders,
    SUM(CASE WHEN order_value_category = 'Low Value' THEN amount ELSE 0 END) AS total_low_value_orders
FROM orders_derived
GROUP BY order_year, order_month;

```
5. Schedule Task for Data Refresh:
```sql
CREATE OR REPLACE TASK refresh_orders_agg
WAREHOUSE = 'COMPUTE_WH'
SCHEDULE = '2 MINUTE'
AS
ALTER DYNAMIC TABLE orders_aggregated REFRESH;

-- Start the task
ALTER TASK refresh_orders_agg RESUME;

```
---------------------------------------------------------------------------------------------------------------------

## Snowflake Queries
- View raw order data:
```sql
SELECT * FROM raw_orders;

```

- View derived data:
```sql
SELECT * FROM orders_derived;

```

- View aggregated data:
```sql
SELECT * FROM orders_aggregated;

```

- Check task history:
```sql
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(TASK_NAME=>'refresh_orders_agg')) ORDER BY SCHEDULED_TIME;

```
