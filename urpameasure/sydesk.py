

from __future__ import annotations

import logging
from typing import Optional
from .urpameasure import Urpameasure

import urpa


logger = logging.getLogger(__name__)


class Sydesk(Urpameasure):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def __new__(cls, *args, **kwargs) -> Sydesk:
        """Prevent user from creating more than one instance of this class"""
        logger.warning("One instance of class Sydesk already exists. Reference to it will be used")
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def add(
        self,
        id: str,
        source_id: str,
        default_value: float = 0,
        default_expiration: int = 60 * 60,
        default_description: Optional[str] = None
    ) -> None:
        """[summary]

        Args:
            id (str): [description]
            source_id (str): [description]
            default_value (float): [description]
            default_expiration (int): [description]
            default_description (Optional[str], optional): [description]. Defaults to None.
        """
        if id in self.measurements:
            raise KeyError(f"Measurement with id '{id}' already exists")

        if len(source_id) > 32:
            raise ValueError("string source_id can't be longer than 32 characters")

        self.measurements[id] = {
            "source_id": source_id,
            "default_value": default_value,
            "default_expiration": default_expiration,
            "default_description": default_description

        }

    def write(
        self,
        id,
        value = 0,
        expiration = 0,
        description = None
    ) -> None:
        """[summary]

        Args:
            id ([type]): [description]
            description ([type]): [description]
            directory ([type], optional): [description]. Defaults to None.
            source_id ([type], optional): [description]. Defaults to None.
            value (int, optional): [description]. Defaults to 0.
            expiration (int, optional): [description]. Defaults to 0.
        """
        if not id in self.measurements:
            raise KeyError(f"Measurement with id '{id}' does not exist")

        this_measurement = self.measurements[id]
        urpa.write_sydesk_measure(
            self.directory,
            this_measurement["source_id"],
            value or this_measurement["default_value"],
            expiration or this_measurement["default_expiration"],
            description or this_measurement["default_description"]
        )

    def _send_login_measure(self, id: str, value: float, expiration: int = 0, description: Optional[str] = None):
        this_measurement = self.measurements[id]
        urpa.write_sydesk_measure(
            self.directory,
            this_measurement["source_id"],
            value,
            expiration or this_measurement["default_expiration"],
            description or this_measurement["default_description"]

        )
