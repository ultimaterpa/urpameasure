from __future__ import annotations
from typing import Optional, Any
import logging

import urpa
from .urpameasure import Urpameasure
from .globals import *
from .utils import check_valid_status

logger = logging.getLogger(__name__)


class Console(Urpameasure):
    instance = None

    def __init__(self):
        """[summary]"""
        super().__init__()

    def __new__(cls, *args: Any, **kwargs: Any) -> Console:
        """Prevent user from creating more than one instance of this class"""
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        else:
            logger.warning("One instance of class Console already exists. Reference to it will be used")
        return cls.instance

    def add(
        self,
        id: str,
        default_status: str = NONE,
        default_name: str = "0 Unnamed measurement", # TODO consider defaulting to 'id'
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
        if not default_name[0].isnumeric():
            if strict_mode:
                raise ValueError(
                    "String arg 'default_name' must start with a number.\nIf you don't want to use a number at the beginning of 'default_name' use arg 'strict_mode=False'"
                )
            else:
                logger.warning("String arg 'default_name' doesn't start with a number")
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
        id,
        status: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        tolerance: Optional[float] = None,
        description: Optional[str] = None,
        precision: Optional[int] = None,
    ) -> None:
        """Writes a measurement to Management Console

        Args:
            id ([type]): Unique id of this measurement
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
        # use either user supplied value or default value that was defined in self.add method
        print(f"value {value}")
        print(value or this_measurement["default_value"] or 0 if value == 0 else 0)
        urpa.write_measure(
            name=name or this_measurement["default_name"],
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

    def clear(self, id: str) -> None:
        """Writes a measurement with all default values

        Args:
            id (str): unique id of this measurement
        """
        # supply no args so it takes all default values
        self.write(id)

    def clear_all(self) -> None:
        """Iterates over all self.measurements and writes default values to them
        """
        for measurement_id in self.measurements:
            self.clear(measurement_id)

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
        if time_unit == "s":
            time_conversion_coeficient = 1
        elif time_unit == "m":
            time_conversion_coeficient = 60
        elif time_unit == "h":
            time_conversion_coeficient = 60 * 60
        else:
            raise ValueError(f"Invalid time unit '{time_unit}'")
        return time_elapsed_seconds / time_conversion_coeficient

    def _send_time_measure(self, id: str, value: float, status: str) -> None:
        """Method called by measure_time decorator

        Args:
            id (str): unique id of the time mesurement
            value (float): time value
            status (str): status of the time measurement to be shown in Management Console
        """
        self.write(id=id, status=status, value=value)

    def _send_login_measure(
        self, id: str, value: float, error_status: str = ERROR, success_status: str = SUCCESS, default_status: str = NONE
    ) -> None:
        """Method called by measure_login decorato

        Args:
            id (str): unique id of the login mesurement
            value (float): value - 0 for ERROR, 100 for SUCCESS, others for undefined (for example for cases where robot did't attempt login yet)
            error_status (str, optional): status to be shown in Console if value is 0. Defaults to ERROR.
            success_status (str, optional): status to be shown in Console if value is 100. Defaults to SUCCESS.
            default_status (str, optional): status to be shown in Console if value is other than 0 or 100. Defaults to NONE.
        """
        status = default_status  # default - may be used as clear state (robot did not attempt to login yet)
        if value == 0:
            status = error_status
        elif value == 100:
            status = success_status
        print(f"login measure {value}")
        self.write(id=id, status=status, value=value)
