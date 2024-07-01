---
title: Overview
description: Provides an overview of how the package works
---

This page provides an overview of how the package internally works. See the
[Getting Started](/guides/getting-started) guide for a quick introduction to
dagster jobs.

## Dynamic jobs

Dagster jobs are compiled by calling [`OpDefinition`](https://docs.dagster.io/_apidocs/ops#dagster.OpDefinition)
and [`GraphDefinition`](https://docs.dagster.io/_apidocs/graphs#dagster.GraphDefinition)
instances within the context of a function decorated by [`@dagster.job`](https://docs.dagster.io/_apidocs/jobs#dagster.job).
Even though runtime calculations using Python-native functions can only occur
inside dagster ops, it is possible to dynamically change how a job is created
using this mechanism.

Consider the following job:

```python
from dagster import job, op

@op
def return_five():
    return 5

@job
def several_calls():
    return_five()
    return_five()
    return_five()
```

This is a job that executes the same op three times. Instead, a Python for loop
could be used to obtain the same behavior:

```python
@job
def several_calls():
    for _ in range(3):
        return_five()
```

Extending this idea further, we may consider the number of calls to
`return_five` to not be fixed. It may instead depend on a value obta\ffined from
elsewhere. To this end a new function is introduced as:

```python
def job_builder(n_calls):
    @job
    def wrapped_job():
        for _ in range(n_calls):
            return_five()

    return wrapped_job
```

This approach is widely used and is known as the factory pattern. A composable
graph builds on this concept by formalizing the interface to the builder and
simplifying the definition of the job.

## Further reading

- *"Factory Patterns in Python"* [on the dagster blog](https://dagster.io/blog/python-factory-patterns).
- *"Unlocking Flexible Pipelines: Customizing the Asset Decorator"* [on the dagster blog](https://dagster.io/blog/unlocking-flexible-pipelines-customizing-asset-decorator).
- *"Abstracting Pipelines for Analysts with a YAML DSL"* [on the dagster blog](https://dagster.io/blog/simplisafe-case-study).
- YAML DSL for Asset Graphs Example [on dagster github](https://github.com/dagster-io/dagster/tree/master/examples/experimental/assets_yaml_dsl).
