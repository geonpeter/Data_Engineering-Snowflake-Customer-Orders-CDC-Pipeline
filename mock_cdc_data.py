import snowflake.connector
import pandas as pd
from datetime import datetime, timedelta
import random
import time

# Snowflake connection parameters
conn = snowflake.connector.connect(
    user='geonpeter',
    password='Pass3010#',
    account='dfjumyd-gl00490',
    warehouse='COMPUTE_WH',
    database='customer_db',
    schema='PUBLIC'
)

# Create a cursor object
cur = conn.cursor()

# Function to generate mock CDC events
def generate_mock_data(order_id=None):
    if order_id is None:
        order_id = f'ORD{random.randint(1, 20)}'  # Use fewer random order_ids
    customer_id = f'CUST{random.randint(1, 100)}'
    order_date = datetime.now() - timedelta(days=random.randint(0, 30))
    status = random.choice(['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED'])
    amount = round(random.uniform(10.0, 500.0), 2)
    product_id = f'PROD{random.randint(1, 50)}'
    quantity = random.randint(1, 10)
    
    return (order_id, customer_id, order_date, status, amount, product_id, quantity)

# Function to insert data into Snowflake
def insert_data_to_snowflake(data):
    cur.execute(
        """
        INSERT INTO customer_orders (order_id, customer_id, order_date, status, amount, product_id, quantity) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        data
    )
    conn.commit()
    print(f"Inserted: {data}")

# Function to update data in Snowflake
def update_data_in_snowflake(order_id):
    new_status = random.choice(['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED'])
    new_amount = round(random.uniform(10.0, 500.0), 2)
    new_quantity = random.randint(1, 10)
    
    cur.execute(
        """
        UPDATE customer_orders 
        SET status = %s, amount = %s, quantity = %s 
        WHERE order_id = %s
        """,
        (new_status, new_amount, new_quantity, order_id)
    )
    conn.commit()
    print(f"Updated order_id: {order_id}")

# Function to delete data from Snowflake
def delete_data_from_snowflake(order_id):
    cur.execute(
        """
        DELETE FROM customer_orders 
        WHERE order_id = %s
        """,
        (order_id,)
    )
    conn.commit()
    print(f"Deleted order_id: {order_id}")

# Function to continuously insert data
def continuous_insert():
    try:
        while True:
            data = generate_mock_data()
            print(data)
            insert_data_to_snowflake(data)
            time.sleep(5)  # Wait for 5 seconds before the next insert
    except KeyboardInterrupt:
        print("Stopping data generation...")
    finally:
        cur.close()
        conn.close()

# Start continuous insert
if __name__ == "__main__":
    #continuous_insert()
    update_data_in_snowflake('ORD12')
    update_data_in_snowflake('ORD2')
# Example usage of update and delete functions
# You can call these functions as needed for ad hoc updates and deletes
# update_data_in_snowflake('ORD1')
# delete_data_from_snowflake('ORD3')