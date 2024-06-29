import re


def convert_to_snake_case(input_string: str) -> str:
    # Step 1: Convert to lowercase
    string = input_string.lower()

    # Step 2: Replace spaces and hyphens with underscores
    string = re.sub(r"[\s-]+", "_", string)

    # Step 3: Remove any characters that are not alphanumeric or underscore
    string = re.sub(r"[^a-z0-9_]", "", string)

    # Step 4: Replace consecutive underscores with a single underscore
    string = re.sub(r"_+", "_", string)

    # Step 5: Remove leading and trailing underscores
    string = string.strip("_")

    # Step 6: If the string is empty or starts with a digit, prepend an underscore
    if not string or string[0].isdigit():
        string = f"_{string}"

    return string
