# urpameasure
Easy measure for UltimateRPA

Can be used with Management Console and Sydesk

## Basic usage
The urpameasure module provides higher order functionality for sending measurements with UltimateRPA robots. It encapsulates classes for working with both measurement variants - Management Console and Sydesk.

### Working with Management Console
First, we need to create the Measurement object
```python
import urpameasure

Measurement = urpameasure.Console()
```

then we can start adding metrics we want to measure
```python
Measurement.add("login", default_name="01 Login Measurement")
Measurement.add("processed", default_unit="%")
Measurement.add("time", default_unit="seconds")
```

lastly, all there is to do is to write the measurements. Login and time measurements can be written via decorator
```python
@Mmeasurement.measure_login("login")
def login():
    pass

@Measurement.measure_time("time")
def main():
    login()
    for i in range(1, 101):
        measumerent.write("processed", value=i)
```

### Working with Sydesk
Working with Sydesk is almost same as working with Console. Only differences are in arguments the measurement accepts.
All possible arguments are described in [Documentation](#Documentation) section of this document
```python
import urpameasure

Measurement = urpameasure.Sydesk()

Measurement.add("some measurement", "SYDESK_SOURCE_ID")
Measurement.add("another measurement", "ANOTHER_SYDESK_SOURCE_ID", default_description="foo bar")

Measurement.write("some measurement", value=5)
Measurement.write("another measurement", value=2, expiration=5)
```

## Documentation
The module has two main classes: `Console` and `Sydesk` for working with Management Console and Sydesk respectively.
Both classes are very similar. They differ only in measurement values that can be written with them.

### Class Console
Creating instance:
```python
import urpameasure

Measurement = urpameasure.Console()
```

Adding metrics:
```python
Measurement.add(
    "measure id"
    default_status=urpameasure.INFO,
    default_name="01 My measurement",
    default_value=0,
    default_unit="%",
    default_tolerance=0,
    default_description="this is a measurement",
    default_precision=2,
    strict_mode=True,
)
```
Args starting with `default_` are default values used as clear state (see `measurement.clear()`) or values to be written with `measurement.write()` if not provided
- `id` (str): unique id of this measurement
- `default_status` (str, optional): status to be written to Console. Defaults to urpameasure.NONE.
- `default_name` (str, optional): name to be written to Console. Defaults to "0 Unnamed measurement".
- `default_value` (Optional[float], optional): value to be written to Console. Defaults to None.
- `default_unit` (str, optional): unit to be written to Console. Defaults to "".
- `default_tolerance` (float, optional): tolerance to be written to Console. Defaults to 0.
- `default_description` (Optional[str], optional): description to be written to Console. Defaults to None.
- `default_precision` (Optional[int], optional): precision to be written to Console. Defaults to None.
- `strict_mode` (bool, optional): `defalut_name` must start with a digit if enabled. Defaults to True.

Writing measurement:
```python
Measurement.write(
    "measure id",
    status=urpameasure.SUCCESS,
    name="a02 Some measurement",
    value=99.5,
    unit="%",
    tolerance=2,
    description="foo bar",
    precision=2,
    strict_mode=False,
)
```
If some of the keyword args are not provided, `default_xxxx` which was specified with `measurement.add()` call will be used
- `id` ([type]): Unique id of this measurement
- `status` (Optional[str], optional): status to be written to Console. self.measurements[id]["default_status"] is used if not provided.
- `name` (Optional[str], optional): name to be written to Console. self.measurements[id]["default_name"] is used if not provided.
- `value` (Optional[float], optional): value to be written to Console. self.measurements[id]["default_value"] is used if not provided.
- `unit` (str, optional): unit to be written to Console. self.measurements[id]["default_unit"] is used if not provided.
- `tolerance` (Optional[float], optional): tolerance to be written to Console. self.measurements[id]["default_tolerance"] is used if not provided.
- `description` (Optional[str], optional): description to be written to Console. self.measurements[id]["default_description"] is used if not provided.
- `precision` (Optional[int], optional): precision to be written to Console. self.measurements[id]["default_precision"] is used if not provided.
- `strict_mode` (bool, optional): `name` must start with a digit if enabled. Defaults to True.

Clearing measurement:
```python
Measurement.clear("measure id")
```
This method call will set all measurement values to `default_xxxx` values which were specified with `measurement.add()` call

Clearing all measurements
```python
Measurement.clear_all()
```
Iterates over all measurements and sets their values to `default_xxxx`

Change default value of a measurement:
```python
Measurement.edit_default_value("measure id", "default_description", "Edited default description")
```

Measure time decorator:
```python
# first define measurement for sending time
Measurement.add("09 time", default_unit="minutes")

# then decorate a function you want to measure time of execution of
@Measurement.measure_time("09 time", time_unit=urpameasure.MINUTES)
def main():
    pass
```
Note: do not confuse `default_unit` with `time_unit`:
- `default_unit` is string that is displayed in the Management Console frontend
- `time_unit` is unit to be used for time conversion inside the urpameasure module. Defaults to urpameasure.SECONDS

Measure login decorator:
```python
@Measurement.measure_login("01 login")
def login():
    pass
```
Sends value 100 - SUCCESS if execution of function `login()` finishes.
Sends value 0 - ERROR if exception is raised during execution of function `login()`

`measure_login()` decorator has three optional keyword argumensts:
- error_status - defaults to urpameasure.ERROR (status to be displayed if login value is 0)
- success_status - defaults to urpameasure.SUCCESS (status to be displayed if login value is 100)


### Class Sydesk
Creating instance:
```python
import urpameasure

Measurement = urpameasure.Sydesk("/path/to/directory")
```

Adding metrics:
```python
Measurement.add(
    "measure id"
    "source id"
    default_value=0,
    default_expiration=60 * 60,
    default_description="this is a measurement"
)
```
- `id` (str): Unique id of this measurement
- `source_id` (str): String Data source ID in SyDesk
- `default_value` (float): Value to be written to Sydesk. Defaults to 0
- `default_expiration` (int): Expiration of the measurement in Sydesk in seconds. Defaults to 3600
- `default_description` (Optional[str], optional): Description of the measurement. Defaults to None.

Writing measurement:
```python
Measurement.write(
    "measure id"
    value=1.5,
    expiration=2,
    description="foo bar"
)
```
- `id` (str): Unique id of this measurement
- `value` (float, optional): Value to be written to Sydesk. self.measurements[id]["default_value"] is used if not provided. Defaults to 0
- `expiration` (int, optional): Expiration of the measurement in Sydesk in seconds. self.measurements[id]["default_expiration"] is used if not provided. Defaults to 0.
- `description` ([type], optional): Description of the measurement. self.measurements[id]["default_description"] is used if not provided. Defaults to None.

Clearing measurement:
```python
Measurement.clear("measure id")
```
This method call will set all measurement values to `default_xxxx` values which were specified with `measurement.add()` call

Clearing all measurements
```python
Measurement.clear_all()
```
Iterates over all measurements and sets their values to `default_xxxx`

Change default value of a measurement:
```python
Measurement.edit_default_value("measure id", "default_value", 100)
```

Measure time decorator:
```python
# first define measurement for sending time
Measurement.add("time")

# then decorate a function you want to measure time of execution of
@Measurement.measure_time("time")
def main():
    pass
```

Measure login decorator:
```python
@Measurement.measure_login("login", expiration=0, description="time measurement")
def login():
    pass
```
keyword arguments `expiration` ad `description` are optional. They default to `0` and `None` respectively

## Examples
### Usage with Management Console
```python
import urpa
import urpameasure

# create Console class instance
Measurement = urpameasure.Console()
# add all desired metrics
Measurement.add("login", default_name="01 App login")
Measurement.add(
    "app_navigation",
    default_status=urpameasure.ERROR,
    default_name="02 App Navigation",
    default_value=0,
    default_unit="%",
    default_tolerance=0,
    default_description="Keeps track of navigation steps trough the app",
    default_precision=2
)
Measurement.add("records_done", default_status=urpameasure.INFO, default_name="03 Percentage done", default_unit="%")
# turn off strict mode so we can use default_name that doesn't start with a digit
Measurement.add("time", default_name="Time elapsed", strcit_mode=False)


@Measurement.measure_login("login")
def login(app):
    app.find_first("Login").send_mouse_click()


@Measurement.measure_time("time")
def main():
    # Clear all measurements. `default_xxxx` values defined with Measure.add() method call will be used
    Measurement.clear_all()
    # Write a measurement to Management Console. All arguments that are not supplied will use values defined with Measure.add() method call
    Measurement.write("app_navigation", value=0)
    app = urpa.open_app(1234)
    # Update a measurement and override some of its default values
    Measurement.write("app_navigation", value=50, description="App opened")
    login(app)
    Measurement.write("app_navigation", value=100, status=urpameasure.SUCCESS)
    for record_index in range(1, 101):
        # do some work here
        Measurement.write("records_done", value=record_index, description=f"Records remaining: {100 - record_index}")
    # We can clear only one measurement at a time
    Measurement.clear("app_navigation")
    # We can edit some of its default values that are used as a clear state
    Measurement.edit_dfefault_value("app_navigation", "default_unit", "Procenta")
    Measurement.cleat("app_navigation")
```

### Take more control over login and time function decorators - Management Console
```python
# We can override statuses which by default are SUCCESS for value 100, ERROR for value 0 and NONE for values other than 0 and 100
# Values 0 and 100 are implicitly written by this function decorator (0: exception was raised, 100: exception was not raised)
@Measurement.measure_login("login", error_status=urpameasure.WARNING, success_status=urpameasure.INFO)
def login(app):
    # We can write arbitrary value to login measure to hint some other state than success/error
    Measurement.write("login", value=50, status: urpameasure.NONE, description="The robot did not attempt login yet")
    app.find_first("Login").send_mouse_click()


# Time units can be urpameasure.SECONDS, urpameasure.MINUTES, urpameasure.HOURS
# The time conversion is done automaticaly based on this value
@Measurement.measure_time("time", time_units=urpameasure.MINUTES, status=urpameasure.NONE)
def main():
    pass
```

### Take more control over login and time function decorators - Sydesk
```python
# We can override expiration and description
@Measurement.measure_login("login", expiration=2, description="A login success measurement")
def login(app):
    app.find_first("Login").send_mouse_click()


@Measurement.measure_time("time", expiration=2, description="A time measurement")
def main():
    pass
```

## Custom Errors
- `MeasurementIdExistsError` - Raised when user tries to add another measurement wit id that already exists
- `InvalidMeasurementIdError` - Raised when user tries to access a measurement with id taht does not exist
- `SourceIdTooLongError` - Only for Sydesk: raised when user tries to define source_id longer than 32 characters