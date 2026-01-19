
Changelog
=========

Version 1.0.6 - 2025-01-19
--------------------

Fixed
^^^^^

* Install numpy 2.2.6. New versions appear to be incompatible with pandera 0.20.40
* Add missing packages polars, azure-identity used by ebmgeodist

Added
^^^^^

* Add ebm-geodist launch script


Version 1.0.4 - 2025-12-09
--------------------

Fixed
^^^^^

* Fixed building groups (non_residential, residential) not accepted by validator in energy_need_improvements.csv
* Fix by where the wrong value is selected from energy_need_improvements.csv when using building groups


Version 1.0.3 - 2025-11-25
--------------------

Fixed
^^^^^

* Corrected issue where ebm-calibrate failed to load calibration year

Added
^^^^^

* Added command line arguments for ebm-calibrate
* Added ``--calibration-year``
* Added ``--version``
* Added ``--help``
* Updated documentation with sections on how to run the calibration, command line arguments and environment variables
* Calibration year will now be written to the calibration spreadsheet




Version 1.0.2 - 2025-11-18
--------------------

Fixed
^^^^^

* Corrected issue preventing loading of area forecast when running ebm-calibrate


Version 1.0.1 - 2025-10-28
--------------------
Added
^^^^^

* Included previously omitted data files in ``ebm geodist``.

Fixed
^^^^^

* Corrected issue where the ``--open`` argument did not work on macOS and Linux. `GitHub PR #1 <https://github.com/NVE/ebm/pull/1>`_


Version 1.0.0 - 2025-10-14
--------------------

* Initial release of ebm.



.. |date| date::

Last Updated on |date|.

Version: |version|.
