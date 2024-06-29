import dataclasses
from typing import Any, ClassVar, Dict, List, LiteralString, Tuple

import dagster
import pydantic
import pydantic.alias_generators

DEFAULT_OUTPUT_KEY_NAME: LiteralString = "result"
DEFAULT_OUTPUT_POINTER: LiteralString = f"/{DEFAULT_OUTPUT_KEY_NAME}"


class ApplicationModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True
    )


class Metadata(ApplicationModel):
    name: str


class OperationDef(ApplicationModel):
    name: str
    function: str


class InputDefinition(ApplicationModel):
    node: str
    pointer: str = DEFAULT_OUTPUT_POINTER


class DependencyDefinition(ApplicationModel):
    name: str
    inputs: List[str | InputDefinition]


class GraphSpec(ApplicationModel):
    initial_data: Dict[str, Any]
    operations: List[OperationDef]
    dependencies: List[DependencyDefinition]


class GraphDefinition(ApplicationModel):
    api_version: ClassVar[LiteralString] = "truevoid.dev/v1alpha1"
    kind: ClassVar[LiteralString] = "ComposableGraph"
    metadata: Metadata
    spec: GraphSpec


@dataclasses.dataclass
class Graph:
    initial_data: Dict[str, Any]
    operations: Dict[str, dagster.GraphDefinition | dagster.OpDefinition]
    dependencies: Dict[str, List[Tuple[str, str | None]]]
