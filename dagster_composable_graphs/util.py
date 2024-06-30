import importlib
import re
from typing import Any, Callable


def to_snake_case(input_string: str) -> str:
    """Convert a string to snake case satisfying regexp `^[A-Za-z0-9_]+$`."""

    # Step 1: Insert underscore before any uppercase letter that follows a
    # lowercase letter or number
    string = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", input_string)

    # Step 2: Convert to lowercase
    string = string.lower()

    # Step 3: Replace spaces, hyphens, and other non-alphanumeric characters
    # (except underscores) with underscores
    string = re.sub(r"[^a-z0-9_]+", "_", string)

    # Step 4: Replace consecutive underscores with a single underscore
    string = re.sub(r"_+", "_", string)

    # Step 5: Remove leading and trailing underscores
    string = string.strip("_")

    # Step 6: If the string is empty or starts with a digit, prepend an
    # underscore
    if not string or string[0].isdigit():
        string = f"_{string}"

    return string


def load_function(function_path: str) -> Callable[..., Any]:
    """
    Return a dynamically loaded function from the given path.

    Raises `ImportError` if the module is not found and `AttributeError` if the
    function is not found.

    Arguments
    ---------
    function_path : str
        Path to the function in `package.module.function` format.

    Returns
    -------
    Callable[..., Any]
        The loaded function.
    """

    *module_parts, function_name = function_path.split(".")
    module_path = ".".join(module_parts)

    try:
        module = importlib.import_module(module_path)
        return getattr(module, function_name)

    except ImportError as exc:
        raise ImportError(f"Could not import module '{module_path}'") from exc

    except AttributeError as exc:
        raise AttributeError(
            f"Function '{function_name}' not found in module '{module_path}'"
        ) from exc
