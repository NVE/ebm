
AreaParameters
==============

.. csv-table:: AreaParameters schema
   :header: "Field", "Type", "Description"

   "Filename", "area_parameters.csv", ""

DataFrameModel for area parameters.


Attributes
----------
building_category : Series[str]
     building category with a custom3 check
      * Require a known building category (house, apartment_block, kindergarten, office, hotel, school, nuring_home, hospital, university, �)
      * or a known building group (non-commercial, commercial)
      * or default
TEK : Series[str]
    TEK values with a custom2 check.
     * A string
     * The value must contain the text TEK.
area : Series[float]
    The area of of a certain building_category and TEK in the model start year. Usually in m�
     * A float using a decimal point ('.') as the separator
     * Area values that must be equal to or greater than 0.

Fields
------

.. csv-table:: Fields in AreaParameters
   :header: "Field", "Type", "Description"

   "building_category", "pandera.typing.pandas.Series[str]", "str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'."
   "TEK", "pandera.typing.pandas.Series[str]", "str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'."
   "area", "pandera.typing.pandas.Series[float]", "str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'."

Checks and Requirements
-----------------------

