import importlib
from pathlib import Path
from typing import Any, Callable, Dict

import dagster
import jsonpointer
import yaml

from .jobs import op_static_value_builder
from .models import DEFAULT_OUTPUT_KEY_NAME, DEFAULT_OUTPUT_POINTER, Graph, GraphDefinition
from .util import convert_to_snake_case


def load_function(function_path: str) -> Callable:
    """
    Dynamically load a function from a given path.

    :param function_path: A string representing the full path to the function.
                          Format: 'package.module.submodule.function'
    :return: The loaded function
    """

    *module_parts, function_name = function_path.split(".")
    module_path = ".".join(module_parts)

    try:
        module = importlib.import_module(module_path)
        return getattr(module, function_name)

    except ImportError:
        raise ImportError(f"Could not import module '{module_path}'")

    except AttributeError:
        raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'")


def load_dagster_graph_definition(
    function_path: str,
) -> dagster.GraphDefinition | dagster.OpDefinition:
    graph_def = load_function(function_path)
    assert isinstance(graph_def, (dagster.GraphDefinition, dagster.OpDefinition))
    return graph_def


def dictify_graph_output(out: Any) -> Dict[str, Any]:
    if hasattr(out, "_asdict"):
        return out._asdict()

    if not isinstance(out, dict):
        return {DEFAULT_OUTPUT_KEY_NAME: out}

    return out


def create_graph_from_def(graph_def: GraphDefinition) -> Graph:
    operations = {
        op.name: load_dagster_graph_definition(op.function) for op in graph_def.spec.operations
    }

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
        operations=operations, dependencies=dependencies, initial_data=graph_def.spec.initial_data
    )


def evaluate_node(graph: Graph, node: str, results: Dict[str, Any]) -> Dict[str, Any]:
    if node in results:
        return results[node]

    if node not in graph.dependencies or not graph.dependencies[node]:
        result = graph.operations[node].alias(node)()

    else:
        input_values = []
        for dep, pointer in graph.dependencies[node]:
            dep_result = evaluate_node(graph, dep, results)
            input_values.append(jsonpointer.resolve_pointer(dep_result, pointer))

        result = graph.operations[node].alias(node)(*input_values)

    result = dictify_graph_output(result)

    results[node] = result

    return result


def evaluate_graph(graph: Graph) -> Dict[str, Any]:
    results = {
        k: dictify_graph_output(op_static_value_builder(k, v)())
        for k, v in graph.initial_data.items()
    }

    for node in graph.operations:
        evaluate_node(graph, node, results)

    return results


def load_graph_def_from_yaml(file_path: str | Path) -> GraphDefinition:
    graph_def = GraphDefinition.model_validate(yaml.safe_load(Path(file_path).read_text()))

    return graph_def


def compose_job(graph_def: GraphDefinition) -> dagster.JobDefinition:
    graph = create_graph_from_def(graph_def)

    @dagster.job(name=convert_to_snake_case(graph_def.metadata.name))
    def composed_job() -> None:
        evaluate_graph(graph)

    return composed_job
