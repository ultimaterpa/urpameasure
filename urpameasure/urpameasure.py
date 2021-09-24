"""Module containig base class for Console and Sydesk classes"""

import logging
import os

import time

from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Union, Any

from .globals import *
from .utils import check_valid_status, check_name

logger = logging.getLogger(__name__)


class Urpameasure(ABC):
    def __init__(self):
        """init"""
        self.measurements = {}

    def __new__(cls):
        """Called when creating new instance

        Raises:
            TypeError: when instancing this class directly (only child classes may be instanced)

        Returns:
            Console or Sydesk: object
        """
        if cls is Urpameasure:
            raise TypeError("Base class Urpameasure can't be instantiated")
        return object.__new__(cls)

    def edit_default_value(
        self, id: str, value_key: str, new_value: Union[str, int, float, None], strict_mode: bool = True
    ) -> None:
        """Edits default value of an existing measurement

        Args:
            id (str): unique id of this measurement
            value_key (str): key of the value to be edited
            new_value (str): value of the new value

        Raises:
            InvalidMeasurementIdError: provided measurement id does not exist
            KeyError: provided measurement id does not contain desired key
            SourceIdTooLongError: source_id is longer than 32 characters
        """
        if not id in self.measurements:
            raise InvalidMeasurementIdError(id)
        if not value_key in self.measurements[id].keys():
            raise KeyError(
                f"Invalid key '{value_key}'. Please use one of the following: '{self.measurements[id].keys()}'"
            )
        # these two are only for Console
        # no need for checking if instance is Console because Sydesk does not have
        # "default_name" and "default_status". So if user tries to edit them on Sydesk it never gets here.
        # ---> KeyError is raised above
        if value_key == "default_name":
            check_name(new_value, strict_mode)
        if value_key == "default_status":
            check_valid_status(new_value)
        if value_key == "source_id" and len(new_value) > 32:
            raise SourceIdTooLongError

        self.measurements[id][value_key] = new_value

    def _touch_time_measure_file(self) -> None:
        """Creates a file with time value written in it"""
        if not os.path.isfile(MEASURE_TIME_FILE_NAME):
            with open(MEASURE_TIME_FILE_NAME, "w") as file:
                file.write(str(time.time()))

    def _start_time_measure(self) -> None:
        """Starts time measuring by creating measure_file"""
        self._touch_time_measure_file()

    @abstractmethod
    def _send_time_measure(self, *args: Any) -> None:
        """Placeholder method to be overriden from child classes"""
        return

    @abstractmethod
    def _send_login_measure(self, *args: Any) -> None:
        """Placeholder method to be overriden from child classes"""
        return

    @abstractmethod
    def _get_measured_time(self, *args: Any) -> float:
        """Reads content of the measure_file and subtracts it from current time

        Args:
            unit (str): Time unit. Used only for Console ("s", "m", "h")

        Returns:
            float: calculated time
        """
        with open(MEASURE_TIME_FILE_NAME, "r") as file:
            start_value = float(file.read())
        time_elapsed_seconds = time.time() - start_value
        return time_elapsed_seconds

    @abstractmethod
    def write(self, *args: Any) -> None:
        """Placeholder method to be overriden from child classes"""
        return

    def _remove_time_measure_file(self) -> None:
        """Removes file with time measure after it is no longer needed"""
        if os.path.isfile(MEASURE_TIME_FILE_NAME):
            os.remove(MEASURE_TIME_FILE_NAME)

    def clear(self, id: str) -> None:
        """Writes a measurement with all default values

        Args:
            id (str): unique id of this measurement
        """
        # supply no args so it takes all default values
        self.write(id)

    def clear_all(self) -> None:
        """Iterates over all self.measurements and writes default values to them"""
        for measurement_id in self.measurements:
            self.clear(measurement_id)

    def measure_time(self, id, time_unit: str = SECONDS, **kwargs: Any) -> Callable:
        """decorator
        kwargs for console: status
        kwargs for sydesk: expiration, description
        """
        if time_unit != SECONDS:
            # used only for management console
            if self.__class__.__name__ != "Sydesk":
                possible_units = (SECONDS, MINUTES, HOURS)
                if time_unit not in possible_units:
                    raise ValueError(
                        f"Invalid time unit '{time_unit}'. Please use one of the following: '{possible_units}'"
                    )
            else:
                logger.warning("Setting time_unit for Sydesk measurement has no effect. It accepts seconds only")

        def wrapper(func):
            @wraps(func)
            def inner():
                self._start_time_measure()
                func()
                self._send_time_measure(id, self._get_measured_time(time_unit), **kwargs)
                self._remove_time_measure_file()

            return inner

        return wrapper

    def measure_login(self, id: str, **kwargs: Any) -> Callable:
        """decorator
        kwargs for console: error_status, success_status
        kwargs for sydesk: expiration, description
        """

        def wrapper(func):
            @wraps(func)
            def inner():
                try:
                    func()
                except Exception as error:
                    self._send_login_measure(id, 0, **kwargs)
                    raise error
                else:
                    self._send_login_measure(id, 100, **kwargs)

            return inner

        return wrapper
