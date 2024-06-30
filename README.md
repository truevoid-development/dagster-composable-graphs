# Dagster Composable Graphs

[Dagster](https://github.com/dagster-io/dagster) is a cloud-native data
pipeline orchestrator for the whole development lifecycle, with integrated
lineage and observability, a declarative programming model, and best-in-class
testability.

This library provides additional functionality to define dagster jobs from a
file in `.yaml` format.

For example, the following definition

```yaml
apiVersion: truevoid.dev/v1alpha1
kind: ComposableGraph
metadata:
  name: concatenate-graphs
spec:
  inputs:
    x: 2.0
    y: 5.0
  operations:
    - name: add_and_multiply
      function: example.jobs.add_and_multiply
    - name: add
      function: example.jobs.add
    - name: multiply
      function: example.jobs.multiply
  dependencies:
    - name: add_and_multiply
      inputs:
        - x
        - y
    - name: add
      inputs:
        - node: add_and_multiply
          pointer: /add
        - x
    - name: multiply
      inputs:
        - y
        - node: add_and_multiply
          pointer: /multiply
```

Results in the job:

![example-job](assets/images/graph.png)
