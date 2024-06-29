from pathlib import Path

import dagster

from dagster_composable_graphs.compose import compose_job, load_graph_def_from_yaml

defs = dagster.Definitions(
    jobs=[compose_job(load_graph_def_from_yaml(Path(__file__).parent / "concat_graphs.yaml"))]
)
