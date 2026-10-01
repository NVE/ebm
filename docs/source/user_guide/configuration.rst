Model configuration
=============================

This page describes the environment variables used to configure the model. 
The configuration of the ``ebm`` and ``ebmgeodist`` modules is controlled through a set of environment variables.
These variables define model execution settings, logging configuration, input and output paths, and other parameters.
They can be provided either via the system environment or through a local ``.env`` file in the working directory.
Unless specified otherwise, the variables are optional and have default values.
However, the ``ebmgeodist`` module requires additional variables to be set, as described below.

General environment variables
-------------------------------
The following environment variables are common for both the ``ebm`` and ``ebmgeodist`` modules:

.. csv-table:: General environment variables
   :file: ../tables/general_env_vars.csv
   :header-rows: 1

EBM geographical distribution specific environment variables
---------------------------------------------------------------

The ``ebmgeodist`` extends the ``ebm`` module by adding functionality for distributing energy use forecasts at the municipality level.
It requires additional configuration variables that identify the Azure Data Lake Storage location of the ELHUB dataset.

.. csv-table:: EBM geographical distribution specific environment variables
   :file: ../tables/ebmgeodist_env_vars.csv
   :header-rows: 1

Authentication is performed via the Azure CLI. Before running ``ebmgeodist`` with ``--source azure``, run ``az login`` and
make sure the signed-in account has read access to the storage account above (e.g. the ``Storage Blob Data Reader`` role
or equivalent ACL/group membership). Contact your Azure administrator if unsure.

Example of a .env file
--------------------------
An example of a ``.env`` configuration file is shown below:

.. code-block:: yaml

      # General EBM settings
      DEBUG=false
      LOG_FORMAT="<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>"
      EBM_INPUT_DIRECTORY=/data/ebm/input
      EBM_OUTPUT_DIRECTORY=/data/ebm/output
      EBM_DEFAULT_INPUT=/data/ebm/default-input
      EBM_ALWAYS_OPEN=false

      # EBMGeoDist module
      EBM_STORAGE_ACCOUNT=mystorageaccount
      EBM_STORAGE_CONTAINER=elhub
      EBM_ELHUB_DATASET=forbruk_per_time_prisomraade_kommune_naeringshovedgruppe

.. note::
      
      - The variables are case-sensitive and should be defined in uppercase letters as shown.
      - The ``.env`` file may contain environment-specific values (e.g. your Azure storage account name) and should never be committed to version control.
      - If a variable is not set, the model will use the default value specified in the tables above.
      - Ensure that the paths provided for input and output directories exist and are accessible by the model.
      - The Elhub dataset path must point to a valid Parquet file containing the necessary data for calculating distribution keys.
      - The logging format used by the EBM and EBMGeoDist modules is based on the Loguru logging framework.
      - The ``LOG_FORMAT`` environment variable allows customization of how log messages are rendered in the console, including timestamps, 
        elapsed time, log level, function name, line number, and message content.

.. |date| date::

Last Updated on |date|.

Version: |version|.
