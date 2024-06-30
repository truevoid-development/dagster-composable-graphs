import re

import pytest

from dagster_composable_graphs.util import load_function, to_snake_case


def _is_valid_snake_case(string: str):
    return bool(re.match(r"^[A-Za-z0-9_]+$", string))


@pytest.mark.parametrize(
    "input_string, expected_output",
    [
        ("Hello World", "hello_world"),
        ("This is a Test", "this_is_a_test"),
        ("123 ABC", "_123_abc"),
        ("Special@#$Characters", "special_characters"),
        ("camelCase", "camel_case"),
        ("snake_case", "snake_case"),
        ("  Multiple   Spaces  ", "multiple_spaces"),
        ("", "_"),
        ("A", "a"),
        ("a-b-c", "a_b_c"),
        ("ALL CAPS", "all_caps"),
        ("mix123ed_CASE", "mix123ed_case"),
        ("___leading_underscores", "leading_underscores"),
        ("trailing_underscores___", "trailing_underscores"),
        ("__double__underscores__", "double_underscores"),
        ("12345", "_12345"),
        ("!@#$%^&*()", "_"),
        ("CamelCaseWithNumbers123", "camel_case_with_numbers123"),
        ("   ", "_"),
        ("kebab-case-example", "kebab_case_example"),
        ("PascalCaseExample", "pascal_case_example"),
        ("1startWithNumber", "_1start_with_number"),
        ("endWithNumber5", "end_with_number5"),
        ("snake_case_with_123_numbers", "snake_case_with_123_numbers"),
        ("ACRONYMS_like_NASA_and_FBI", "acronyms_like_nasa_and_fbi"),
    ],
)
def test_to_snake_case(input_string: str, expected_output: str) -> None:
    """Test that function `to_snake_case` returns the expected output."""

    result = to_snake_case(input_string)

    assert result == expected_output
    assert _is_valid_snake_case(
        result
    ), f"Output '{result}' does not match the required regex pattern"
    assert result.islower() or result.startswith(
        "_"
    ), f"Output '{result}' is not in snake_case (should be all lowercase or start with underscore)"
    assert (
        "_" not in result[1:] or result[1:].islower()
    ), f"Output '{result}' is not in snake_case (contains uppercase after first character)"


def test_load_function() -> None:
    """Test all branches of function `load_function`."""

    # Test successful function loading
    loaded_func = load_function("os.path.join")
    assert callable(loaded_func)
    assert loaded_func.__name__ == "join"

    # Test ImportError
    with pytest.raises(ImportError, match="Could not import module 'non_existent_module'"):
        load_function("non_existent_module.some_function")

    # Test AttributeError
    with pytest.raises(
        AttributeError, match="Function 'non_existent_function' not found in module 'os'"
    ):
        load_function("os.non_existent_function")

    # Test function with multiple module parts
    loaded_func = load_function("os.path.join")
    assert callable(loaded_func)
    assert loaded_func.__name__ == "join"
