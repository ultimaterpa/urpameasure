from .globals import *


def check_valid_status(status: str) -> None:
    """Checks whether 'status' is a string accepted by the Management Console

    Args:
        status (str): string representing status to be checked

    Raises:
        ValueError: if status is invalid
    """
    possible_statuses = (SUCCESS, WARNING, ERROR, INFO, NONE)
    if not status in possible_statuses:
        raise ValueError(f"Invalid status '{status}'. Please use one of the following: '{possible_statuses}'")