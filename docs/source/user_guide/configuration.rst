Model configuration
=============================

This page describes the environment variables used to configure the model. 
The configuration of the ebm and ebmgeodist modules is controlled through a set of environment variables.
These variables define model execution settings, logging configuration, input and output paths, and other parameters.
They can be provided either via the system environment or through a local ``.env`` file in the working directory.
Unless specified otherwise, the variables are optional and have default values.
However, the ``ebmgeodist`` requires additional variables to be set, as described below.

General environment variables
-------------------------------
The following environment variables are common for both the ``ebm`` and ``ebmgeodist`` modules:

.. csv-table:: General environment variables
   :file: ..\tables\general_env_vars.csv
   :header-rows: 1

EBM geographical distribution specific environment variables
---------------------------------------------------------------

The ``ebmgeodist`` extends the ``ebm`` module by adding functionality for distributing energy use forecasts at the municipality level.
It requires one additional configuration variable to locate the underlying Elhub dataset.

.. csv-table:: EBM geographical distribution specific environment variables
   :file: ..\tables\ebmgeodist_env_vars.csv
   :header-rows: 1

Example of a .env file
--------------------------
An example of a ``.env`` configuration file is shown below:

.. code-block:: yaml

      # General EBM settings
      DEBUG=false
      LOG_FORMAT="<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>"
      EBM_INPUT_DIRECTORY=/data/ebm/input
      EBM_OUTPUT_DIRECTORY=/data/ebm/output
      EBM_DEFAULT_INPUT=baseline_input.csv
      EBM_ALWAYS_OPEN=false

      # EBMGeoDist module
      EBM_GEODIST_ELHUB_LOCATION=/data/elhub/elhub_data.parquet      


.. |date| date::

Last Updated on |date|.

Version: |version|.