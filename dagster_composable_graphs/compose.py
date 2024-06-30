from pathlib import Path
from typing import Any, Dict

import dagster
import jsonpointer
import yaml

from .jobs import input_op_builder
from .models import (
    DEFAULT_INITIAL_DATA_NAME,
    DEFAULT_OUTPUT_KEY_NAME,
    DEFAULT_OUTPUT_POINTER,
    Graph,
    GraphDefinition,
)
from .util import load_function, to_snake_case


def load_definition(
    function_path: str,
) -> dagster.GraphDefinition | dagster.OpDefinition:
    """
    Return a dynamically loaded dagster op or graph definition from the given path.

    Dynamically loads a dagster `GraphDefinition` or `OpDefinition` in the
    provided `function_path`. See Documentation of function `load_function` for
    more details.

    Arguments
    ---------
    function_path : str
        Path to the function in `package.module.function` format.

    Returns
    -------
    dagster.GraphDefinition | dagster.OpDefinition
        The graph or op definition.
    """

    graph_def = load_function(function_path)
    assert isinstance(graph_def, (dagster.GraphDefinition, dagster.OpDefinition))
    return graph_def


def dictify_graph_output(out: Any, key: str = DEFAULT_OUTPUT_KEY_NAME) -> Dict[str, Any]:
    """
    Convert the provided value into a dictionary if it is not one.

    Function intended to be used with outputs of dagster `OpDefinition` or
    `GraphDefinition` evaluations when building the dagster execution graph.

    When the definition evaluation returns a single element, it is wrapped in a
    dictionary with a predetermined key set by constant
    `DEFAULT_OUTPUT_KEY_NAME`.

    When the definition returns multiple outputs it has method `_asdict`, which
    is used here to directly convert it to a dictionary with keys that can be
    referenced from the dependency definition.

    Arguments
    ---------
    out : Any
        The result of evaluating the op or graph definition.

    key : str
        Key used in the dictionary when op or graph evaluation returns a single
        element.

    Returns
    -------
    Dict[str, Any]
        Dictionary as described above.
    """

    if hasattr(out, "_asdict"):
        return out._asdict()

    return {key: out}


def create_graph_from_def(graph_def: GraphDefinition) -> Graph:
    """Return a `Graph` object constructed from its definition.

    After defining a composable graph this function iterates over the
    dependencies, converting them into nodes.

    Arguments
    ---------
    graph_def : GraphDefinition
        Definition of the composable graph.

    Returns
    -------
    Graph
        The processed graph.
    """

    operations = {op.name: load_definition(op.function) for op in graph_def.spec.operations}

    dependencies = {}
    for dep in graph_def.spec.dependencies:
        node_deps = []
        for input_def in dep.inputs:
            if isinstance(input_def, str):
                node_deps.append((input_def, DEFAULT_OUTPUT_POINTER))
            else:
                node_deps.append((input_def.node, input_def.pointer))

        dependencies[dep.name] = node_deps

    return Graph(
        operations=operations, dependencies=dependencies, initial_data=graph_def.spec.inputs
    )


def evaluate_node(graph: Graph, node: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single node in a graph.

    This function is called for each operation in a `Graph` object. If the
    operation has not been visited before, the corresponding dagster
    `OpDefinition` or `GraphDefinition` is invoked.

    Note that this function is intended to be evaluated inside a function
    decorated by `@dagster.job`.

    Arguments
    ---------
    graph : Graph
        Processed graph, typically created by function `create_graph_from_def`.

    node : str
        Name of the node currently being processed. Must be defined in
        `graph.operations`. If it is not present in `graph.dependencies` it is
        considered to not have any dependencies.

    results : Dict[str, Any]
        Dictionary containing outputs of node evaluations.

    Returns
    -------
    Dict[str, Any]
        Output of evaluating this node, processed by function `dictify_graph_output`.
    """

    if node in results:
        return results[node]

    if node not in graph.dependencies or not graph.dependencies[node]:
        # IF the node does not have any dependencies it can be directly
        # invoked.
        result = graph.operations[node].alias(node)()

    else:
        # If the node does have dependencies they are loaded and resolved, then
        # passed as positional arguments.

        input_values = []

        for dep, pointer in graph.dependencies[node]:
            dep_result = evaluate_node(graph, dep, results)

            if isinstance(dep_result, dict):
                input_values.append(jsonpointer.resolve_pointer(dep_result, pointer))
            else:
                input_values.append(dep_result)

        result = graph.operations[node].alias(node)(*input_values)

    results[node] = dictify_graph_output(result)
    return results[node]


def evaluate_graph(graph: Graph) -> Dict[str, Any]:
    """
    Iterate over operations in the `graph` evaluating nodes.

    This function generates the initial data from the graph definition and then
    evaluates all operations in the graph.

    Arguments
    ---------
    graph : Graph
        Processed graph, typically created by function `create_graph_from_def`.

    Returns
    -------
    Dict[str, Any]
        Output of evaluating every node in the graph.
    """

    results = dictify_graph_output(input_op_builder(DEFAULT_INITIAL_DATA_NAME, graph.initial_data)())

    for node in graph.operations:
        evaluate_node(graph, node, results)

    return results


def load_graph_def_from_yaml(file_path: str | Path) -> GraphDefinition:
    """
    Load a `GraphDefinition` from a file in `.yaml` format.

    Arguments
    ---------
    file_path : str | Path
        Path to the file to load.

    Returns
    -------
    GraphDefinition
        The definition of the graph.
    """

    return GraphDefinition.model_validate(yaml.safe_load(Path(file_path).read_text()))


def compose_job(graph_def: GraphDefinition) -> dagster.JobDefinition:
    """
    Compile a graph definition into a dagster `JobDefinition.

    Given the provided `GraphDefinition`, this function generates a dagster job
    from it.
    """

    graph = create_graph_from_def(graph_def)

    @dagster.job(name=to_snake_case(graph_def.metadata.name))
    def composed_job() -> None:
        evaluate_graph(graph)

    return composed_job
