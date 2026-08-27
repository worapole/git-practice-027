# test_join.py
def test_two_dataframes_can_join(spark):
    sales_customers = spark.createDataFrame(
        [(1, "Alice"), (2, "Bob"), (3, "Carol")],
        ["customerID", "first_name"],
    )
    orders = spark.createDataFrame(
        [(1, "A-100", 50.0), (2, "B-200", 99.0)],
        ["customer_id", "order_id", "amount"],
    )

    result = customers.join(orders, on="customer_id", how="inner")

    # Force execution and pull results back to the driver
    rows = result.collect()

    assert result.count() == 2                        # only matched customers
    assert set(result.columns) == {"customer_id", "name", "order_id", "amount"}

    matched = {(r["customer_id"], r["order_id"]) for r in rows}
    assert matched == {(1, "A-100"), (2, "B-200")}    # Carol (id 3) dropped, no order
