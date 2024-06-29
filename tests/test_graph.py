from pathlib import Path

from dagster_composable_graphs.compose import compose_job, load_graph_def_from_yaml

data_path = Path(__file__).parent / "data"


def test_job_creation() -> None:
    """Tests programmatic construction of a job from several graphs."""

    compose_job(load_graph_def_from_yaml(data_path / "test_graph.yaml"))
