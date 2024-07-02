---
title: Advanced Usage
description: Guide exemplifying advanced uses of the library
sidebar:
    order: 10
---

This guide provides several examples of advanced functionality provided by the
library. See the code [on Github](https://github.com/truevoid-development/dagster-composable-graphs/tree/feat/add-docs/examples/advanced_usage).

## Using JSON pointers

A **JSON Pointer**[^1] defines a string syntax for identifying a specific value
within a JavaScript Object Notation (JSON) document. This library uses JSON
pointers to refer to keys in the dictionary returned by dagster ops and graphs
when they return multiple outputs.

Consider the following definitions:

```python title="add_and_multiply.py"
@dagster.op()
def add(x: float, y: float) -> float:
    """Return the sum of the provided numbers."""

    return x + y


@dagster.op()
def multiply(x: float, y: float) -> float:
    """Return the product of the provided numbers."""

    return x * y


@dagster.graph(
    out={
        "sum": dagster.GraphOut("Sum of the numbers."),
        "product": dagster.GraphOut("Product of the numbers."),
    },
)
def add_and_multiply(x: float, y: float) -> Dict[str, float]:
    """Return both the sum and product of the provided numbers."""

    return {"sum": add(x, y), "product": multiply(x, y)}
```

Here we have a graph returning two outputs: `"add"` and `"multiply"`. To define
a composable graph that evaluates op `add` on the output of `add_and_multiply`
we would use JSON pointers as follows:

```yaml
apiVersion: truevoid.dev/v1alpha1
kind: ComposableGraph
metadata:
  name: json-pointer
spec:
  inputs:
    value1: 2.0
    value2: 5.0
  operations:
    - name: add_and_multiply
      function: example.jobs.add_and_multiply
    - name: add
      function: example.jobs.add
    - name: add_and_multiply
      inputs:
        - value1
        - value2
    - name: add
      inputs:
        - node: add_and_multiply
          pointer: /sum             # 👈 here.
        - node: add_and_multiply
          pointer: /product         # 👈 and here.
```

In this way we indicate that the inputs of op `add` are obtained from the
dictionary that graph `add_and_multiply` returns. Note that even though JSON
pointers allow referencing arbitrarily nested dictionaries dagster always
returns a flat key-value pair map in which values are op or graph evaluations.

For the moment there is no validation that the pointers resolve to anything,
raising an exception when the dagster code location is loaded.

## Further reading

- [More information on dagster op outputs](https://docs.dagster.io/concepts/ops-jobs-graphs/ops#outputs).
- [More information on multiple dagter graph outputs](https://docs.dagster.io/concepts/ops-jobs-graphs/nesting-graphs#multiple-outputs).
- [JSON Pointer practical guide (Java)](https://www.baeldung.com/json-pointer).
- [`jsonpointer` package](https://github.com/stefankoegl/python-json-pointer).

[^1]: [JSON Pointer (RFC 6901)](https://tools.ietf.org/html/rfc6901).
