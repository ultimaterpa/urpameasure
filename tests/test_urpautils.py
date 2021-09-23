"""Module containing all tests for urpameasure"""
from contextlib import nullcontext as does_not_raise_error
import pytest
from freezegun import freeze_time

import urpameasure


class Test_console:
    """[summary]"""

    def test_add(self):
        measure = urpameasure.Console()
        assert not measure.measurements
        measure.add("a measurement")
        assert len(measure.measurements) == 1
        measure.add(
            "another measurement",
            default_status=urpameasure.ERROR,
            default_name="02 App Navigation",
            default_value=0,
            default_unit="%",
            default_tolerance=0,
            default_description="Keeps track of navigation steps trough the app",
            default_precision=2,
        )
        assert len(measure.measurements) == 2
        # check both measurement have correct default values
        this_measurement = measure.measurements["a measurement"]
        assert this_measurement["default_status"] == urpameasure.NONE
        assert this_measurement["default_name"] == "0 Unnamed measurement"
        assert this_measurement["default_value"] is None
        assert this_measurement["default_unit"] is None
        assert this_measurement["default_tolerance"] == 0
        assert this_measurement["default_description"] is None
        assert this_measurement["default_precision"] is None
        this_measurement = measure.measurements["another measurement"]
        assert this_measurement["default_status"] == urpameasure.ERROR
        assert this_measurement["default_name"] == "02 App Navigation"
        assert this_measurement["default_value"] == 0
        assert this_measurement["default_unit"] == "%"
        assert this_measurement["default_tolerance"] == 0
        assert this_measurement["default_description"] == "Keeps track of navigation steps trough the app"
        assert this_measurement["default_precision"] == 2
        # try adding measurement with existing id
        with pytest.raises(KeyError):
            measure.add("a measurement")
        # test ValueError for adding invalid status and invalid name in strict mode
        with pytest.raises(ValueError):
            measure.add("abc", default_status="ab")
        with pytest.raises(ValueError):
            measure.add("abc", default_name="ab")

    def test_edit_default_value_errors(self):
        measure = urpameasure.Console()
        measure.add("measurement")
        with pytest.raises(KeyError):
            measure.edit_default_value("different measurement", "", "")
        with pytest.raises(KeyError):
            # invalid key
            measure.edit_default_value("measurement", "value", "")
        with pytest.raises(KeyError):
            # key that should only work with Sydesk
            measure.edit_default_value("measurement", "default_expiration", "")

    @pytest.mark.parametrize(
        "key,value",
        [
            ("default_name", "05 name"), # TODO az dodelam cekovani strict modu do tyhle metody tak tady na to udelej taky test (pripadne spis ho dej o metodu vejs kde se testujou errory)
            ("default_status", urpameasure.INFO),
            ("default_value", 5.2),
            ("default_unit", "abc"),
            ("default_tolerance", 3),
            ("default_description", "fsdfname"),
            ("default_precision", 5),
        ],
    )
    def test_edit_default_value(self, key, value):
        measure = urpameasure.Console()
        measure.add("measurement")
        measure.edit_default_value("measurement", key, value) # TODO "measurement" dej nekam do konstanty protze to pouzivas na plno mistech
        assert measure.measurements["measurement"][key] == value

    def test_write(self):
        # can't really test writing correct values to Console;
        # atleast test raiseng correct errors
        measure = urpameasure.Console()
        measure.add("measurement")
        with pytest.raises(ValueError):
            measure.write("different measurement")
        with pytest.raises(ValueError):
            measure.write("measurement", status="abc")
        with pytest.raises(ValueError):
            measure.write("measurement", name="abc")
        with does_not_raise_error():
            measure.write("measurement", name="abc", strict_mode=False)

    def test_measure_time(self):
        measure = urpameasure.Console()
        # simulate how the measure_time decorator works
        measure._remove_time_measure_file()
        with freeze_time("2012-01-14 15:30"):
            measure._start_time_measure()
        with freeze_time("2012-01-14 15:31"):
            assert measure._get_measured_time("s") == 60
            measure._remove_time_measure_file()
        # try different units
        with freeze_time("2012-01-14 15:30"):
            measure._start_time_measure()
        with freeze_time("2012-01-14 16:30"):
            assert measure._get_measured_time("m") == 60
            assert measure._get_measured_time("h") == 1
            with pytest.raises(ValueError):
                # invalid time unit
                measure._get_measured_time("a")
            measure._remove_time_measure_file()

    @pytest.mark.skip(reason="idk how to test this or even if I should")
    def test_measure_login(self):
        """test measure_login decorator"""


class Test_sydesk:
    pass


class Test_miscs:
    """[summary]"""

    def test_parent_class_instancing(self):
        with pytest.raises(TypeError):
            urpameasure.Urpameasure()

    ######## TODO probably move these two to test_console since they are not used with sydesk.... but than again they are not Console() methods soooo..... #####
    @pytest.mark.parametrize(
        "status,expected",
        [
            ("SUCCESS", does_not_raise_error()),
            (urpameasure.SUCCESS, does_not_raise_error()),
            ("WARNING", does_not_raise_error()),
            ("ERROR", does_not_raise_error()),
            ("INFO", does_not_raise_error()),
            ("NONE", does_not_raise_error()),
            ("success", pytest.raises(ValueError)),
            ("abc", pytest.raises(ValueError)),
            (123, pytest.raises(ValueError)),
        ],
    )
    def test_status_validation(self, status, expected):
        with expected:
            urpameasure.check_valid_status(status)

    @pytest.mark.parametrize(
        "name,strict_mode,expected",
        [
            ("01 measurement", True, does_not_raise_error()),
            ("measurement", True, pytest.raises(ValueError)),
            ("01 measurement", False, does_not_raise_error()),
            ("measurement", False, does_not_raise_error()),
        ],
    )
    def test_measurement_name(self, name, strict_mode, expected):
        with expected:
            urpameasure.check_name(name, strict_mode)

    ##############################################################################################################################################
