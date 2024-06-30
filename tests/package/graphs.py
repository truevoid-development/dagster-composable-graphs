from typing import Any, Dict, Iterator

import dagster


@dagster.op()
def return_two() -> int:
    """Return number `2`."""

    return 2


@dagster.op()
def multiply(x: Any, y: Any) -> Any:
    """Multiply two values."""

    return x * y


@dagster.op(out={"out0": dagster.Out(int), "out1": dagster.Out(int)})
def return_multiple() -> Iterator[dagster.Output]:
    """Return multiple outputs."""

    yield dagster.Output(5, "out0")
    yield dagster.Output(7, "out1")


@dagster.graph(out={"out0": dagster.GraphOut("out0"), "out1": dagster.GraphOut("out1")})
def return_multiple_graph() -> Dict[str, int]:
    """Return multiple outputs from a graph."""

    return return_multiple()
