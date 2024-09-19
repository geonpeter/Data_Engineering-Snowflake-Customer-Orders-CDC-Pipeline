CREATE DATABASE Ecomm;

USE Ecomm;

CREATE OR REPLACE TABLE raw_orders (
    order_id STRING,
    customer_id STRING,
    order_date TIMESTAMP,
    status STRING,
    amount NUMBER,
    product_id STRING,
    quantity NUMBER
);

-- DROP TABLE raw_orders;

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
    CASE
        WHEN amount > 100 THEN 'High Value'
        ELSE 'Low Value'
    END AS order_value_category,
    CASE
        WHEN status = 'DELIVERED' THEN 'Completed'
        ELSE 'Pending'
    END AS order_completion_status,
    DATEDIFF('day', order_date, CURRENT_TIMESTAMP()) AS days_since_order
FROM raw_orders;

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

SELECT * FROM raw_orders;

SELECT * FROM orders_derived;

SELECT * FROM orders_aggregated;

CREATE OR REPLACE TASK refresh_orders_agg
WAREHOUSE = 'COMPUTE_WH'
SCHEDULE = '2 MINUTE'
AS
ALTER DYNAMIC TABLE orders_aggregated REFRESH;

ALTER TASK refresh_orders_agg RESUME;

--ALTER TASK refresh_orders_agg SUSPEND;

SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(TASK_NAME=>'refresh_orders_agg')) ORDER BY SCHEDULED_TIME;