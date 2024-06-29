from typing import Any, Dict, Iterator

import dagster


@dagster.op()
def return_two() -> int:
    return 2


class MultiplyConfig(dagster.Config):
    factor: int = 3


@dagster.op()
def multiply(config: MultiplyConfig, number: int) -> int:
    return number * config.factor


@dagster.op(out={"add": dagster.Out(int), "multiply": dagster.Out(int)})
def add_and_multiply(x: int, y: int) -> Iterator[dagster.Output]:
    yield dagster.Output(x + y, "add")
    yield dagster.Output(x * y, "multiply")


@dagster.graph()
def return_and_multiply() -> int:
    return multiply(return_two())


@dagster.graph(out={od.name: dagster.GraphOut() for od in add_and_multiply.output_defs})
def combined_multiply(x: int, y: int) -> Dict[str, int]:
    return add_and_multiply(x, y)


@dagster.graph()
def calculate_multiply(value: int) -> int:
    return multiply(value)


@dagster.op()
def report_value(value: int) -> str:
    print(value)

    return f"{value}"


@dagster.op()
def log_value(context: dagster.OpExecutionContext, value: Any) -> None:
    context.log.info(value)


@dagster.graph()
def result_report(value: int) -> str:
    return report_value(value)


@dagster.job()
def calculate_two() -> None:
    out1 = return_and_multiply()
    result_report.alias("report1")(out1)
    result_report.alias("report2")(out1)
