"""Module containing global constants"""

MEASURE_TIME_FILE_NAME: str = "time.measure"

# probably TODO move statuses and time units to dataclasses ???
SUCCESS: str = "SUCCESS"
WARNING: str = "WARNING"
ERROR: str = "ERROR"
INFO: str = "INFO"
NONE: str = "NONE"

SECONDS: str = "s"
MINUTES: str = "m"
HOURS: str = "h"


class MeasurementIdExistsError(KeyError):
    """Error raised when user tries to add a measurement with already existing id"""

    def __init__(self, id: str):
        """init

        Args:
            id (str): string id of the measurement to be swown in the error message
        """
        super().__init__(f"Measurement with id '{id}' already exists!")


class InvalidMeasurementIdError(KeyError):
    """Error raised when user tries to write a measurement with non-existing id"""

    def __init__(self, id: str):
        """init

        Args:
            id (str): string id of the measurement to be swown in the error message
        """
        super().__init__(f"Measurement with id '{id}' does not exist!")


class SourceIdTooLongError(ValueError):
    """Error raised when user tries to define the Sydesk source_id longer than 32 chars"""

    def __init__(self) -> None:
        super().__init__("String source_id can't be longer than 32 characters.")