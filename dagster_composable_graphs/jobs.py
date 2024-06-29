from typing import Any

import dagster

from .util import convert_to_snake_case


def op_static_value_builder(name: str, static_value: Any) -> dagster.OpDefinition:
    @dagster.op(
        name=convert_to_snake_case(name),
        ins={"value": dagster.In(type(static_value))},
        out=dagster.Out(type(static_value)),
        description=(
            f"Returns input data `{name}` static value `{static_value}`. "
            "May be overridden in the run configuration."
        ),
    )
    def op_fn(value: Any = static_value):
        return value

    return op_fn
