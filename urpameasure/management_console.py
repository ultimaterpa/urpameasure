from __future__ import annotations
from typing import Optional, Any
import logging

import urpa
from .urpameasure import Urpameasure
from .globals import *
from .utils import check_valid_status

logger = logging.getLogger(__name__)


class Console(Urpameasure):

    def __init__(self):
        """[summary]"""
        super().__init__()

    # TODO why tho? why cant i have two instances? one for e.g. time and login and other for metrics? ...... probably delete this
    # def __new__(cls, *args: Any, **kwargs: Any) -> Console:
    #     """Prevent user from creating more than one instance of this class"""
    #     if not isinstance(cls.instance, cls):
    #         cls.instance = object.__new__(cls)
    #     else:
    #         logger.warning("One instance of class Console already exists. Reference to it will be used")
    #     return cls.instance

    def add( # maybe TODO here and in write() - force arg types that Console accepts
        self,
        id: str,
        default_status: str = NONE,
        default_name: str = "0 Unnamed measurement",  # TODO consider defaulting to 'id'
        default_value: Optional[float] = None,
        default_unit: Optional[str] = None,
        default_tolerance: float = 0,
        default_description: Optional[str] = None,
        default_precision: Optional[int] = None,
        strict_mode: bool = True,
    ) -> None:
        """[summary]

        Args:
            id (str): unique id of this measurement
            default_status (str, optional): status to be written to Console if none provided. Defaults to NONE.
            default_name (str, optional): name to be written to Console if none provided. Defaults to "0 Unnamed measurement".
            default_value (Optional[float], optional): value to be written to Console if none provided. Defaults to None.
            default_unit (str, optional): unit to be written to Console if none provided. Defaults to "".
            default_tolerance (float, optional): tolerance to be written to Console if none provided. Defaults to 0.
            default_description (Optional[str], optional): description to be written to Console if none provided. Defaults to None.
            default_precision (Optional[int], optional): precision to be written to Console if none provided. Defaults to None.
            strict_mode (bool, optional): name must start with a digit if enabled. Defaults to True.

        Raises:
            KeyError: attempted to add a measurement with id that already exists
            ValueError: name does not start with a digit in strict mode
        """
        check_valid_status(default_status)
        if id in self.measurements:
            raise KeyError(f"Measurement with id '{id}' already exists")
        check_name(default_name, strict_mode)
        self.measurements[id] = {
            "default_name": default_name,
            "default_status": default_status,
            "default_value": default_value,
            "default_unit": default_unit,
            "default_tolerance": default_tolerance,
            "default_description": default_description,
            "default_precision": default_precision,
        }

    def write(
        self,
        id: str,
        status: Optional[str] = None,
        name: Optional[str] = None,  # TODO add strict mode
        value: Optional[float] = None,
        unit: Optional[str] = None,
        tolerance: Optional[float] = None,
        description: Optional[str] = None,
        precision: Optional[int] = None,
        strict_mode: bool = True,
    ) -> None:
        """Writes a measurement to Management Console

        Args:
            id (str): Unique id of this measurement
            status (Optional[str], optional): status to be written to Console. self.measurements[id]["default_status"] is used if not provided. Defaults to None.
            name (Optional[str], optional): name to be written to Console. self.measurements[id]["default_name"] is used if not provided. Defaults to None.
            value (Optional[float], optional): value to be written to Console. self.measurements[id]["default_value"] is used if not provided. Defaults to None.
            unit (str, optional): unit to be written to Console. self.measurements[id]["default_unit"] is used if not provided. Defaults to "".
            tolerance (Optional[float], optional): tolerance to be written to Console. self.measurements[id]["default_tolerance"] is used if not provided. Defaults to None.
            description (Optional[str], optional): description to be written to Console. self.measurements[id]["default_description"] is used if not provided. Defaults to None.
            precision (Optional[int], optional): precision to be written to Console. self.measurements[id]["default_precision"] is used if not provided. Defaults to None.

        Raises:
            ValueError: measurement with provided id dos not exist
        """
        if status:
            check_valid_status(status)
        if not id in self.measurements:
            raise ValueError(f"Invalid measurement id '{id}'")
        this_measurement = self.measurements[id]
        name = name or this_measurement["default_name"]
        check_name(name, strict_mode)
        # use either user supplied value or default value that was defined in self.add method
        urpa.write_measure(
            name=name,
            status=status or this_measurement["default_status"],
            # cannot use simple 'or' for value because '0' can be valid measurement
            value=value if value is not None else this_measurement["default_value"],
            unit=unit or this_measurement["default_unit"],
            # cannot use simple 'or' for tolerance because '0' can be valid value for it
            tolerance=tolerance if tolerance is not None else this_measurement["default_tolerance"],
            description=description or this_measurement["default_description"],
            precision=precision or this_measurement["default_precision"],
            id=id,
        )

    def _get_measured_time(self, time_unit: str) -> float:
        """Calls super's _get_measured_time method and converts its output based on 'unit'

        Args:
            time_unit (str): "s" - seconds, "m" - minutes, "h" - hours

        Raises:
            ValueError: time_unit is not "s", "m" or "h"

        Returns:
            float: measured time in desired units
        """
        time_elapsed_seconds = super()._get_measured_time()
        if time_unit == SECONDS:
            time_conversion_coeficient = 1
        elif time_unit == MINUTES:
            time_conversion_coeficient = 60
        elif time_unit == HOURS:
            time_conversion_coeficient = 60 * 60
        else:
            raise ValueError(f"Invalid time unit '{time_unit}'")
        return time_elapsed_seconds / time_conversion_coeficient

    def _send_time_measure(self, id: str, value: float, status: str = INFO) -> None:
        """Method called by measure_time decorator

        Args:
            id (str): unique id of the time mesurement
            value (float): time value
            status (str): status of the time measurement to be shown in Management Console
        """
        check_valid_status(status) # TODO do this everywhere where status is supplied as an arg
        self.write(id=id, status=status, value=value)

    def _send_login_measure(
        self,
        id: str,
        value: float,
        error_status: str = ERROR,
        success_status: str = SUCCESS, # TODO for example here lmao   (hint: read previous todo)
    ) -> None:
        """Method called by measure_login decorato

        Args:
            id (str): unique id of the login mesurement
            value (float): value - 0 for ERROR, 100 for SUCCESS, others for undefined (for example for cases where robot did't attempt login yet)
            error_status (str, optional): status to be shown in Console if value is 0. Defaults to ERROR.
            success_status (str, optional): status to be shown in Console if value is 100. Defaults to SUCCESS.
        """
        if value == 0:
            status = error_status
        elif value == 100:
            status = success_status
        else:
            raise ValueError(f"This should not have happened. Login measure value is not 0 or 100: '{value}'")
        self.write(id=id, status=status, value=value)


def check_name(name: str, strict_mode: bool):
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
                "String arg 'default_name' must start with a number.\nIf you don't want to use a number at the beginning of 'default_name' use arg 'strict_mode=False'"
            )
        else:
            logger.warning("String arg 'default_name' doesn't start with a number")
