# Example Package

This package showcases how a job could be created from existing ops and graphs.
File [`jobs.py`](jobs.py) implements dagster ops and graphs, file
[`concat_graphs.yaml`](concat_graphs.yaml) defines their dependencies, and
[`code_location.py`](code_location.py) generates the job.
