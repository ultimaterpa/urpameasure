from __future__ import annotations
from typing import Optional

import urpa
import urpameasure


class Console(urpameasure.Urpameasure):
    instance = None

    def __init__(self):
        """[summary]"""
        # super().__init__()
        self.measurements = {}

    def __new__(cls, *args, **kwargs) -> Console:
        """Prevent user from creating more than one instance of this class"""
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def add(
        self,
        id: str,
        name: str = "Unnamed measurement",
        default_value = None,
        unit: Optional[str] = None,
        tolerance: float = 0,
        description: Optional[str] = None,
        precision: Optional[int] = None,
    ) -> None:
        """[summary]

        Args:
            id (str): [description]
            name (str, optional): [description]. Defaults to "Unnamed measurement".
            default_value ([type], optional): [description]. Defaults to None.
            unit (Optional[str], optional): [description]. Defaults to None.
            tolerance (float, optional): [description]. Defaults to 0.
            description (Optional[str], optional): [description]. Defaults to None.
            precision (Optional[int], optional): [description]. Defaults to None.

        Raises:
            KeyError: [description]
        """
        # TODO enforce number at the beggining of 'name' (or atleast warn the user) ---- idk maybe both and define strict/unstrict mode?
        if id in self.measurements:
            raise KeyError(f"Measurement with id '{id}' already exists")
        self.measurements[id] = {
            "name": name,
            "value": default_value,
            "unit": unit,
            "tolerance": tolerance,
            "description": description,
            "precision": precision,
        }

    def write(
        self,
        id,
        status,
        name: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        tolerance: Optional[float] = None,
        description: Optional[str] = None,
        precision: Optional[int] = None,
    ) -> None:
        """[summary]

        Args:
            id ([type]): [description]
            status ([type]): [description]
            name (Optional[str], optional): [description]. Defaults to None.
            value (Optional[float], optional): [description]. Defaults to None.
            unit (Optional[str], optional): [description]. Defaults to None.
            tolerance (Optional[float], optional): [description]. Defaults to None.
            description (Optional[str], optional): [description]. Defaults to None.
            precision (Optional[int], optional): [description]. Defaults to None.
        """
        possible_statuses = ("SUCCESS", "WARNING", "ERROR", "INFO", "NONE")
        if not status in possible_statuses:
            raise ValueError(f"Invalid status '{status}'. Please use one of the following: '{possible_statuses}'")
        if not id in self.measurements:
            raise ValueError(f"Invalid measurement id '{id}'")
        this_measurement = self.measurements[id]
        urpa.write_measure(
            name=name or this_measurement["name"],
            status=status,
            value=value or this_measurement["value"],
            unit=unit or this_measurement["unit"],
            tolerance=tolerance or this_measurement["tolerance"],
            description=description or this_measurement["description"],
            precision=precision or this_measurement["precision"],
            id=id,
        )

    def clear(self, id: str, zero_value: Optional[float] = None) -> None:
        """[summary]

        Args:
            id (str): [description]
            zero_value (Optional[float], optional): [description]. Defaults to None.
        """
        urpa.write_measure(
            name=self.measurements[id]["name"],
            status="NONE",
            value=zero_value or self.measurements[id]["value"],
            id=id
        )

    def clear_all(self) -> None:
        for measurement in self.measurements:
            # measurement["value"] is value that was set in self.add method via default_value arg
            self.clear(measurement["id"])

    def _send_time_measure(self, id , value) -> None:
        self.write(id=id, status="INFO", value=value)


