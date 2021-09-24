"""Module containing universally used functions"""

import logging

from .globals import *


logger = logging.getLogger(__name__)


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


def check_name(name: str, strict_mode: bool) -> None:
    """Checks whether string 'name' begins with a digit.
    Warns user or waises exception if not - behaviour based on bool 'strict_mode'

    Args:
        name (str): string to be checked
        strict_mode (bool): behavioural flag - raise exception or warn user

    Raises:
        ValueError: If 'name' does not start with a digit and 'strict_mode' is set to True
    """
    if not name[0].isnumeric():
        if strict_mode:
            raise ValueError(
                """String arg 'default_name' must start with a number.
                \rIf you don't want to use a number at the beginning of 'default_name' use arg 'strict_mode=False'"""
            )
        else:
            logger.warning("String arg 'default_name' doesn't start with a number")
