import os

import time

from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional, Union

from .globals import *
from .utils import check_valid_status

class Urpameasure(ABC):
    def __init__(self):
        """[summary]"""
        self.measurements = {}

    def edit_default_value(self, id: str, value_key: str, new_value: Union[str, int, float, None]) -> None:
        """Edits default value of an existing measurement

        Args:
            id (str): unique id of this measurement
            value_key (str): key of the value to be edited
            new_value (str): value of the new value

        Raises:
            KeyError: provided measurement id does not exist
            KeyError: provided measurement id does not contain desired key
        """
        if not id in self.measurements:
            raise KeyError(f"Measurement with id '{id}' does not exist")
        if not value_key in self.measurements[id].keys():
            raise KeyError(f"Invalid key '{value_key}'. Please use one of the following: '{self.measurements[id].keys()}'")
        if value_key == "default_status":
            check_valid_status(new_value)
        self.measurements[id][value_key] = new_value


    def _touch_time_measure_file(self) -> None:
        """[summary]"""
        if not os.path.isfile(MEASURE_TIME_FILE_NAME):
            with open(MEASURE_TIME_FILE_NAME, "w") as file:
                file.write(str(time.time()))

    def _start_time_measure(self):
        self._touch_time_measure_file()

    @abstractmethod
    def _send_time_measure(self, *args) -> None:
        """Placeholder method to be overriden from child classes"""
        return

    @abstractmethod
    def _send_login_measure(self, *args) -> None:
        return

    @abstractmethod
    def _get_measured_time(self, *args) -> float:
        """

        Args:
            unit ([type]): [description]

        Returns:
            str: [description]
        """
        with open(MEASURE_TIME_FILE_NAME, "r") as file:
            start_value = float(file.read())
        time_elapsed_seconds = time.time() - start_value
        return time_elapsed_seconds

    def _remove_time_measure_file(self):
        """Removes file with time measure after it is no longer needed"""
        os.remove(MEASURE_TIME_FILE_NAME)

    def measure_time(self, id, status: str = INFO, time_unit: str = "s"):
        """decorator"""
        if time_unit != "s":
            # TODO dont call it unit... console already has arg unit
            # used only for management console
            # setting unit for sydesk has no effect
            possible_units = ("h", "m", "s")
            if time_unit not in possible_units:
                raise ValueError(f"Invalid time unit '{time_unit}'. Please use one of the following: '{possible_units}'")

        def wrapper(func):
            @wraps(func)
            def inner():
                self._start_time_measure()
                func()
                self._send_time_measure(id, self._get_measured_time(time_unit), status)
                self._remove_time_measure_file()

            return inner

        return wrapper

    def measure_login(self, id, **kwargs):
        """decorator
        kwargs for console: error_status, success_status, default_status
        kwargs for sydesk: expiration, description
        """

        def wrapper(func):
            @wraps(func)
            def inner():
                #self._send_login_measure(id, 50, error_status, success_status, default_status)  # reset value - can be anything besides 0 and 100
                try:
                    func()
                except Exception as error:
                    self._send_login_measure(id, 0, **kwargs)
                    raise error
                else:
                    self._send_login_measure(id, 100, **kwargs)

            return inner
        return wrapper
