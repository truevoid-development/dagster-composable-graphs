---
title: Getting Started
description: Example package that creates a dagster job from YAML
---

## Introduction

This guide describes in detail the contents of the `example` package [on Github](https://github.com/truevoid-development/dagster-composable-graphs/tree/feat/add-docs/example)
and introduces dagster concepts.

## Motivation

Let us first motivate the need for this library. Composable graphs
have two important qualities that enable several potential new uses:

1. **Integrated.** Because composable graphs are YAML-based It is possible to
   create dagster jobs from any language. Even within a Python application it
   may be beneficial to define jobs using a more limited API to simplify job
   definition, since more complex jobs may become unmaintainable in part
   because Python-native functionality is used to define them.
1. **Dynamic.** Changing the YAML file and reloading the code location is
   all it takes to update the job. Combined with the fact that the composable
   graph definition may be loaded from any location over the network it is
   possible to dynamically change dagster jobs as needed.

   A possible application of this dynamism is to have a GUI-based job editor to
   enable a no-code approach to defining dagster jobs.

Considering these immediate advantages, the sections below introduce how to
define a job in dagster and using a composable graph.

## Defining a job

In dagster an [op](https://docs.dagster.io/concepts/ops-jobs-graphs/ops#ops) is
the smallest unit of computation. Each op is executed separately and is the
basis of dagster functionality. Ops are arranged in [graphs](https://docs.dagster.io/concepts/ops-jobs-graphs/graphs#op-graphs)
to enable reusability. The main difference between ops and graphs is that the
body of the graph must be entirely composed of dagster ops. That is, it is not
possible to mix dagster ops and Python-defined functions.

Finally these ops and graphs are combined into [dagster jobs](https://docs.dagster.io/concepts/ops-jobs-graphs/op-jobs).
For example:

```python title="jobs.py"
from dagster import job, op, graph


@op
def return_five():
    return 5


@op
def add_one(arg):
    return arg + 1


@graph
def return_six():
    # A graph that combines two ops.
    return add_one(return_five())


@job
def return_seven():
    # To define the job both an op and a graph are used.
    add_one(return_six())
```

Notice that because typically jobs are defined as a Python function it is
difficult to change them at runtime, or create them from programming languages
other than Python.

Once a job is defined as above it is exposed to dagster as part of the [code
location](https://docs.dagster.io/concepts/code-locations). In this minimal
example we create a file named `code_location.py` as follows:

```python title="code_location.py"
from dagster import Definitions

# Assume the file above is a module next to this one.
from .jobs import return_seven

defs = Definitions(jobs=[return_seven])
```

Then start the dagster webserver by running

```bash
dagster dev -f code_location.py
```

Opening then dagster on a browser shows the job we just created.

## Defining a composable graph

Instead of defining the job as Python code we instead write a file in `.yaml`
format with a certain schema. The job above would be defined as:

```yaml title="return_seven.yaml"
apiVersion: truevoid.dev/v1alpha1
kind: ComposableGraph
metadata:
  name: return-seven
spec:
  operations:
    - name: return_six
      function: jobs.return_six
    - name: add_one
      function: jobs.add_one
  dependencies:
    - name: add_one
      inputs:
        - node: return_six
```

Here the two relevant sections are `operations` and `dependencies`. The former
defines nodes in the graph and references the Python function that defines
them. Notice that dagster ops and graphs are both supported. The latter
connects inputs to nodes defined in `operations` to the output of other nodes.

Instead of the code location as presented in the previous section now the job
is instead created as follows:

```python title="code_location.py"
from dagster import Definitions

from dagster_composable_graphs.compose import (
    compose_job,
    load_graph_def_from_yaml,
)

defs = Definitions(
    jobs=[compose_job(load_graph_def_from_yaml("return_seven.yaml"))]
)
```

In this revised version the job is no longer imported but created using
function `compose_job`. Those ops and graphs composed in the job are imported
dynamically using the value provided in field `function`. Because these are
resolved at runtime it is possible to modularize and fully decouple the
definition of ops and graphs from the jobs that execute them. This is
conceptually similar to how assets may be defined in multiple code locations as
described [in the documentation](https://docs.dagster.io/concepts/assets/software-defined-assets#defining-asset-dependencies-across-code-locations).

## Further reading

- Read the post *"Abstracting Pipelines for Analysts with a YAML DSL"* [on the
  dagster blog](https://dagster.io/blog/simplisafe-case-study) that started this idea.
