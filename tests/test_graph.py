from pathlib import Path

from dagster_composable_graphs.compose import compose_job, load_graph_def_from_yaml

data_path = Path(__file__).parent / "data"


def test_job_creation() -> None:
    """Tests programmatic construction of a job from several graphs."""

    job = compose_job(load_graph_def_from_yaml(data_path / "test_graph.yaml"))

    execution = job.execute_in_process()

    assert execution.output_for_node("return_two") == 2  # noqa: PLR2004


def test_input_data() -> None:
    """Tests creation of a job with input data."""

    job = compose_job(load_graph_def_from_yaml(data_path / "test_input.yaml"))

    execution = job.execute_in_process()

    assert execution.output_for_node("multiply") == 50  # noqa: PLR2004


def test_multiple_outputs() -> None:
    """Tests creation of a job with input data."""

    job = compose_job(load_graph_def_from_yaml(data_path / "test_multiple_outputs.yaml"))

    execution = job.execute_in_process()

    assert execution.output_for_node("multiply") == 35  # noqa: PLR2004
