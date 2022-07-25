"""Module containing class for Sydesk measurements"""

from __future__ import annotations

import logging
from typing import Optional, Any
from urpameasure.globals import InvalidMeasurementIdError, MeasurementIdExistsError, SourceIdTooLongError
from .urpameasure import Urpameasure

import urpa


logger = logging.getLogger(__name__)


class Sydesk(Urpameasure):
    def __init__(self, directory):
        """Init"""
        super().__init__()
        self.directory = directory

    def add(
        self,
        id: str,
        source_id: str,
        default_value: float = 0,
        default_expiration: int = 60 * 60,
        default_description: str = "",
    ) -> None:
        """Adds a new measurement to self.measurements

        Args:
            id (str): Unique id of this measurement
            source_id (str): String Data source ID in SyDesk
            default_value (float): Value to be written to Sydesk. Defaults to 0
            default_expiration (int): Expiration of the measurement in Sydesk in seconds. Defaults to 3600
            default_description (str): Description of the measurement. Defaults to empty string.

        Raises:
            MeasurementIdExistsError: measurement with this id already exists
            SourceIdTooLongError: source_id is longer than 32 characters
        """
        if id in self.measurements:
            raise MeasurementIdExistsError(id)

        if len(source_id) > 32:
            raise SourceIdTooLongError

        self.measurements[id] = {
            "source_id": source_id,
            "default_value": default_value,
            "default_expiration": default_expiration,
            "default_description": default_description,
        }

    def write(
        self,
        id: str,
        value: float = 0,
        expiration: int = 0,
        description: Optional[str] = None,
    ) -> None:
        """Writes a measurement to sydesk

        Args:
            id (str): Unique id of this measurement
            value (float, optional): Value to be written to Sydesk. self.measurements[id]["default_value"] is used if not provided. Defaults to 0
            expiration (int, optional): Expiration of the measurement in Sydesk in seconds. self.measurements[id]["default_expiration"] is used if not provided. Defaults to 0.
            description ([type], optional): Description of the measurement. self.measurements[id]["default_description"] is used if not provided. Defaults to None.

        Raises:
            InvalidMeasurementIdError: Measurement with this id does not exist
        """
        if not id in self.measurements:
            raise InvalidMeasurementIdError(id)

        this_measurement = self.measurements[id]
        urpa.write_sydesk_measure(
            self.directory,
            this_measurement["source_id"],
            value or this_measurement["default_value"],
            expiration or this_measurement["default_expiration"],
            description or this_measurement["default_description"],
        )

    def _send_time_measure(self, id: str, value: float, expiration: int = 0, description: Optional[str] = None) -> None:
        """Called by measure_time decorator. Sends time measurement"""
        self.write(id=id, value=value, expiration=expiration, description=description)

    def _send_login_measure(
        self, id: str, value: float, expiration: int = 0, description: Optional[str] = None
    ) -> None:
        """Called by measure_login decorator. Sends login measurement"""
        this_measurement = self.measurements[id]
        urpa.write_sydesk_measure(
            self.directory,
            this_measurement["source_id"],
            value,
            expiration or this_measurement["default_expiration"],
            description or this_measurement["default_description"],
        )

    def _get_measured_time(self, *args: Any) -> float:
        """Calls super's _get_measured_time

        Returns:
            float: measured time in seconds
        """
        return super()._get_measured_time(*args)
