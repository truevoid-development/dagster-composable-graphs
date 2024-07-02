from typing import Dict

import dagster


@dagster.op()
def add(x: float, y: float) -> float:
    """Return the sum of the provided numbers."""

    return x + y


@dagster.op()
def multiply(x: float, y: float) -> float:
    """Return the product of the provided numbers."""

    return x * y


@dagster.graph(
    out={
        "sum": dagster.GraphOut("Sum of the numbers."),
        "product": dagster.GraphOut("Product of the numbers."),
    },
)
def add_and_multiply(x: float, y: float) -> Dict[str, float]:
    """Return both the sum and product of the provided numbers."""

    return {"sum": add(x, y), "product": multiply(x, y)}
