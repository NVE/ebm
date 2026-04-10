
Changelog
=========


Version 1.0.9 - 2026-04-10
--------------------------

Fixed
^^^^^

* Fixes bug #3821 where custom building_code was ignored by energy need input
* Fixes data missing from heating systems shares in for the user case example.
* Fixes #3812 missing version number in documentation introduced by c15e5bfc.


Version 1.0.8 - 2026-03-26
--------------------------

Added
^^^^^

* Adds experimental interface with package energibruksmodell
* Adds various helper functions in energibruksmodell.helpers
* Return more columns in standard output
* Add functions for freezing and stopping s-curves




Version 1.0.6 - 2025-01-19
--------------------------

Fixed
^^^^^

* Install numpy 2.2.6. New versions appear to be incompatible with pandera 0.20.40
* Add missing packages polars, azure-identity used by ebmgeodist

Added
^^^^^

* Add ebm-geodist launch script


Version 1.0.4 - 2025-12-09
--------------------------

Fixed
^^^^^

* Fixed building groups (non_residential, residential) not accepted by validator in energy_need_improvements.csv
* Fix by where the wrong value is selected from energy_need_improvements.csv when using building groups


Version 1.0.3 - 2025-11-25
--------------------------

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
--------------------------

Fixed
^^^^^

* Corrected issue preventing loading of area forecast when running ebm-calibrate


Version 1.0.1 - 2025-10-28
--------------------------
Added
^^^^^

* Included previously omitted data files in ``ebm geodist``.

Fixed
^^^^^

* Corrected issue where the ``--open`` argument did not work on macOS and Linux. `GitHub PR #1 <https://github.com/NVE/ebm/pull/1>`_


Version 1.0.0 - 2025-10-14
--------------------------

* Initial release of ebm.



.. |date| date::

Last Updated on |date|.

Version: |version|.
