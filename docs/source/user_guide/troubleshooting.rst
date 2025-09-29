Troubleshooting
###############


Ebm fail the the error `Input Directory <dirname> Not Found`
============================================================

**Problem**


This error indicates that the input directory specified (or the default input directory) does not exist in your current
working directory.

**Solution 1**


By default, ebm looks for a directory named input. If it doesn't exist, you can create it manually or use the
``--create-input`` flag.

1. To create the default input directory:

.. code-block:: powershell

  ebm --create-input

2. Then run:

.. code-block:: powershell

  ebm


**Solution 2**


1. If you prefer a different directory name (e.g., my-input), create it like this:

.. code-block:: powershell

  ebm --create-input --input=my-input

2. Then run ebm with the same directory:


.. code-block:: powershell

  ebm --input=my-input

.. seealso::

   :ref:`Model configuration`


building_code periods do not overlap failure cases …
====================================================

**Problem**

Some entries in :ref:`building_code_parameters.csv<building_code_parameters>` have overlapping start and end years,
which violates the schema validation.

The full error message may look something like:

.. code-block:: python

   {
     "schema": "building_code_parameters",
     "column": "building_code_parameters",
     "check": "building_code periods do not overlap",
     "error": "DataFrameSchema 'building_code_parameters' failed element-wise validator number 1: building_code periods do not overlap failure cases: TEK10, 2018, 2011, 2021"
   }



**Solution**

1. Open :ref:`building_code_parameters.csv<building_code_parameters>` and adjust the start and end year columns to ensure that no end year overlaps with the start year of the next entry.


.. code-block:: powershell

  start input/building_code_parameters.csv


PermissionError: [Errno 13] Permission denied: 'output\\area.xlsx' (file open)
=================================================================================================

**Problem**

Windows file locking prevents multiple programs from accessing the same file. The output file is likely open in Excel
or another application.

**Solution**

Close Excel and re-run the model.


period_end_year should be greater than period_start_year> failure cases: PRE_TEK49;1945;0;1948"
===============================================================================================

**Problem**

Although the error message suggests a year mismatch, the actual issue is a formatting error in the CSV file—semicolons
are used instead of commas.

**Solution**

Open the invalid input file in a text editor (e.g., Notepad), and replace all semicolons (;) with commas (,).



.. |date| date::

Last Updated on |date|.

Version: |version|.
