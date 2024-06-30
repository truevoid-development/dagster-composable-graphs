from typing import Any, Dict, Iterator

import dagster

from .util import to_snake_case


def input_op_builder(name: str, static_value: Dict[str, Any]) -> dagster.OpDefinition:
    """
    Define a dagster op that returns the input data for a graph.

    This function is used to provide the input data for the composable graph in
    a way that is compatible with the compilation of a dagster `JobDefinition`.

    Input values given in the graph definition may be overridden by the run
    configuration.

    Arguments
    ---------
    name : str
        Name of the created dagster op.

    static_value : Dict[str, Any]
        Dictionary containing input values as provided in the graph definition.

    Returns
    -------
    dagster.OpDefinition
        The generated dagster `OpDefinition`.
    """

    @dagster.op(
        name=to_snake_case(name),
        out={k: dagster.Out(type(v)) for k, v in static_value.items()},
        config_schema={
            k: dagster.Field(type(v), default_value=v, is_required=False)
            for k, v in static_value.items()
        },
        description=(
            f"Return initial values for parameters {', '.join(static_value)}. "
            "May be overridden in the run configuration."
        ),
    )
    def op_fn(context: dagster.OpExecutionContext) -> Iterator[dagster.Output]:
        yield from (
            dagster.Output(context.op_config.get(k, v), output_name=k)
            for k, v in static_value.items()
        )

    return op_fn
