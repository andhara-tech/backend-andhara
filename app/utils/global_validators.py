from fastapi import HTTPException, status


def validate_empty_str(
    value: str, field_name: str = "Value"
) -> None:
    """
    Validates that a given string is not empty or composed solely of whitespace.

    Args:
        value (str): The string value to validate.
        field_name (str, optional): The name of the field being validated. Defaults to "Value".

    Raises:
        HTTPException: If the string is empty or contains only whitespace, an HTTP 400 error is raised
                       with a message indicating that the field cannot be empty.
    """
    if not value.strip():  # This handles empty strings and strings with only whitespace
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} no puede estar vacío/a.",
        )


def validate_list(
    lst: list,
    raise_error: bool = False,
    error_message: str = "La lista no puede estar vacía.",
) -> bool:
    """
    Validates whether a given list is empty.

    This function checks if the provided list is empty and can either raise an HTTPException
    or return a boolean value based on the `raise_error` parameter.

    Args:
        lst (list): The list to validate.
        raise_error (bool, optional): If True, raises an HTTPException when the list is empty. Defaults to False.
        error_message (str, optional): The error message to include in the exception if raised. Defaults to "La lista no puede estar vacía.".

    Returns:
        bool: True if the list is empty, False otherwise.

    Raises:
        HTTPException: If `raise_error` is True and the list is empty, an HTTPException is raised with the provided error message.
    """
    if not lst:
        if raise_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )
        return True  # is empty
    return False  # not empty
