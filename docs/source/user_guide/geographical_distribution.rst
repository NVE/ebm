Geographical distribution
################################
The geographical distribution module ``ebmgeodist`` is an extension of the EBM model that enables the distribution of annual energy use
forecast results from EBM to finer geographical units, such as municipalities in our case.To use the module, you can
follow the instructions below.

Please, open your preferred terminal and follow the instructions below.


Basic usage
============================

The first thing you need to do is to open your preferred terminal. Then, you need to create the necessary input files. To do this, run:

.. code-block:: bash

  python -m ebmgeodist --create-input

The command creates the necessary input files in a new directory called `input` in the current working directory.

To run the actual geographical distribution module, it is sufficient to use the bare command with no options:

.. code-block:: bash

  python -m ebmgeodist

By default, the distribution keys are loaded from `input`, and the results are written to the directory `output`.
If no options are specified, the module distributes energy consumption for all energy products across all building categories at the municipality level. If you want
to distribute a specific energy product, this can be done using the option ``--energy-product``. For example, to distribute
district heating consumption, run: ``--energy-product dh``.

By default and without using any option, the distribution keys are loaded from the input file
``yearly_aggregated_elhub_data.parquet`` under the ``input`` folder.
If the file does not exist, the module will generate the distribution keys using Elhub API inside the module, assuming that you have
access to Elhub data via Azure Blob Storage. 

The results are saved in an Excel file named ``ebmgeodist_output.xlsx`` under the ``output`` folder.

Additional arguments
============================


The module supports several options to customize the distribution process. The available options are summarized in the table below:

.. csv-table:: Geographical distribution overview
   :file: ../tables\ebmgeodist_command_options.csv
   :header-rows: 1

.. note::

    The double dashes ``--`` before each option are required when running the module from the command line. In the table above the double dashes 
    are omitted for better readability. For more detailed information about each option, you can run:

    .. code-block:: bash

      python -m ebmgeodist --help
  
    The option ``local`` means that the distribution keys for electricity will be loaded from the input files under the ``input`` folder, as introduced above.
    The option ``azure`` means that the distribution keys for electricity will be generated using Elhub API inside the module.
    For all other energy products, the distribution keys are always loaded from the input files under the ``input`` folder.

The general syntax for running the module with specific options is as follows:

.. code-block:: python
  
  python -m ebmgeodist <--option> 


.. tip::
    
    The options in the table can be combined. For example, to distribute bioenergy (fuelwood) consumption for residential buildings at the municipality level
    for all years, you can run:
    
    .. code-block:: bash

       python -m ebmgeodist --energy-product fuelwood --building-category residential --years 2022 2023 2024


.. seealso::

   :ref:`Geographical distribution`
        For a more detailed description of the geographical distribution module, including input file formats and examples.

