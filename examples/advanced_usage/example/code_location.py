from pathlib import Path

import dagster

from dagster_composable_graphs import compose_job, load_graph_def_from_yaml

defs = dagster.Definitions(
    jobs=[compose_job(load_graph_def_from_yaml(p)) for p in Path(__file__).parent.glob("*.yaml")]
)
