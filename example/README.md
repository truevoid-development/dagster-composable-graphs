# Example Package

This package showcases how a job could be created from existing ops and graphs.
File [`jobs.py`](example/jobs.py) implements dagster ops and graphs, file
[`concat_graphs.yaml`](example/concat_graphs.yaml) defines their dependencies, and
[`code_location.py`](example/code_location.py) generates the job.

To see it in action, install this package and run start dagster webserver:

```bash
# First set up a venv and activate it
python -m venv venv
source venv/bin/activate

# Then, install the package
pip install poetry
poetry install

# Start the webserver
dagster dev
```
