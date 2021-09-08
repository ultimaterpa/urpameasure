##### NAPADY
# posilani mereni i jako funkce i jako dekorator
# to samy pro mereni casu
import os

import time


MEASURE_TIME_FILE_NAME: str = "time.measure"


class Urpameasure:
    def __init__(self):
        """[summary]"""

    def _touch_time_measure_file(self) -> None:
        """[summary]"""
        if not os.path.isfile(MEASURE_TIME_FILE_NAME):
            with open(MEASURE_TIME_FILE_NAME, "w") as file:
                file.write(str(time.time()))

    def _start_time_measure(self):
        self._touch_time_measure_file()

    def _send_time_measure(self, id, value) -> None:
        """Placeholder method for overriding from child classes"""
        raise RuntimeError("Method _send_time_measure cannot be called on the super class")

    def _get_measured_time(self, unit) -> str:
        """[summary]

        Args:
            unit ([type]): [description]

        Returns:
            str: [description]
        """
        with open(MEASURE_TIME_FILE_NAME, "r") as file:
            start_value = float(file.read())
        time_elapsed_seconds = time.time() - start_value
        if unit == "s":
            time_conversion_coeficient = 1
        elif unit == "m":
            time_conversion_coeficient = 60
        elif unit == "h":
            time_conversion_coeficient = 60 * 60
        else:
            raise ValueError(f"Invalid time unit '{unit}'")
        return str(time_elapsed_seconds / time_conversion_coeficient)

    def _remove_time_measure_file(self):
        """Removes file with time measure after it is no longer needed"""
        os.remove(MEASURE_TIME_FILE_NAME)

    def measure_time(self, id, unit: str = "m"):
        """decorator"""
        possible_units = ("h", "m", "s")
        if unit not in possible_units:
            raise ValueError(f"Invalid time unit '{unit}'. Please use one of the following: '{possible_units}'")

        def inner(func):
            self._start_time_measure()
            func()
            self._send_time_measure(id, self._get_measured_time(unit))
            self._remove_time_measure_file()

        return inner
