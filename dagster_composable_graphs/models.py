import dataclasses
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple

import dagster
import pydantic
import pydantic.alias_generators

DEFAULT_OUTPUT_KEY_NAME: Literal["result"] = "result"
DEFAULT_OUTPUT_POINTER: Literal["/result"] = "/result"
DEFAULT_INITIAL_DATA_NAME: Literal["inputs"] = "inputs"


class ApplicationModel(pydantic.BaseModel):
    """Base model for application-specific models with camel case alias generation."""

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True
    )


class Metadata(ApplicationModel):
    """Metadata information for a graph."""

    name: str = pydantic.Field(description="Name of the graph.")
    annotations: Dict[str, str] = pydantic.Field(
        description="Unstructured key-value map used to populate the job tags.",
        default_factory=dict,
    )


class OperationDef(ApplicationModel):
    """Definition of an operation in the graph."""

    name: str = pydantic.Field(description="Name of the operation.")
    function: str = pydantic.Field(description="Function associated with the operation.")


class InputDefinition(ApplicationModel):
    """Definition of an input for an operation."""

    node: str = pydantic.Field(description="Name of the node providing the input.")
    pointer: str = pydantic.Field(
        default=DEFAULT_OUTPUT_POINTER, description="Pointer to the specific output of the node."
    )


class DependencyDefinition(ApplicationModel):
    """Definition of dependencies for an operation."""

    name: str = pydantic.Field(description="Name of the operation.")
    inputs: List[str | InputDefinition] = pydantic.Field(
        description="List of inputs or input definitions for the operation."
    )


class ResourceDefinition(ApplicationModel):
    """Definition of a reference to a resource definition."""

    name: str = pydantic.Field(description="Name of the resource as used by ops in the job.")
    import_field: str = pydantic.Field(
        description="Importable path to the resource.", alias="import"
    )


class GraphSpec(ApplicationModel):
    """Specification of a graph."""

    description: Optional[str] = pydantic.Field(
        description="Description of the composed job.", default=None
    )
    inputs: Dict[str, Any] = pydantic.Field(
        description="Inputs for the graph.", default_factory=dict
    )
    operations: List[OperationDef] = pydantic.Field(
        description="List of operations in the graph.", default_factory=list
    )
    dependencies: List[DependencyDefinition] = pydantic.Field(
        description="List of dependencies between operations.", default_factory=list
    )
    resources: List[ResourceDefinition] = pydantic.Field(
        description="Resources used in the job.", default_factory=list
    )
    executor: Optional[str] = pydantic.Field(
        description="Importable path to the executor used in this job.", default=None
    )


class GraphDefinition(ApplicationModel):
    """Definition of a composable graph."""

    api_version: ClassVar[Literal["truevoid.dev/v1alpha1"]] = "truevoid.dev/v1alpha1"
    kind: ClassVar[Literal["truevoid.dev/v1alpha1"]] = "ComposableGraph"
    metadata: Metadata = pydantic.Field(description="Metadata for the graph.")
    spec: GraphSpec = pydantic.Field(description="Specification of the graph.")


@dataclasses.dataclass
class Graph:
    """Representation of a graph with its components."""

    initial_data: Dict[str, Any]
    operations: Dict[str, dagster.GraphDefinition | dagster.OpDefinition]
    dependencies: Dict[str, List[Tuple[str, str | None]]]
    resources: Dict[str, dagster.ResourceDefinition | dagster.ConfigurableResource]
    executor: Optional[dagster.ExecutorDefinition]
