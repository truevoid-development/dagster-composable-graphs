from typing import Dict

import dagster


@dagster.op()
def add(x: float, y: float) -> float:
    """Returns the addition of the provided numbers."""

    return x + y


@dagster.op()
def multiply(x: float, y: float) -> float:
    """Returns the product of the provided numbers."""

    return x * y


@dagster.graph(
    out={
        "add": dagster.GraphOut("Sum of the numbers."),
        "multiply": dagster.GraphOut("Product of the numbers."),
    }
)
def add_and_multiply(x: float, y: float) -> Dict[str, float]:
    """Returns both the addition and product of the provided numbers."""

    return {"add": add(x, y), "multiply": multiply(x, y)}
