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

The command creates the necessary input files in a new directory called |input_directory| in the current working directory.

To run the actual geographical distribution module, it is sufficient to use the bare command with no options:

.. code-block:: bash

  python -m ebmgeodist

By default, the distribution keys are loaded from |input_directory|, and the results are written to the |output_directory| directory.
If no options are specified, the module distributes energy consumption for all energy products across all building categories at the municipality level. If you want
to distribute a specific energy product, this can be done using the option ``--energy-product``. For example, to distribute
district heating consumption, run: ``--energy-product dh``.

By default and without using any option, the distribution keys for electricity are calculated inside the module using electricity consumption data from |elhub_aggregated_data_ref| under |input_directory|.
If the file does not exist, the module will generate the distribution keys using Elhub API inside the module, assuming that you have
access to Elhub data via Azure Blob Storage. 

The results are saved in four Excel files named |output_ebmgeodist_ref| under |output_directory|, where ``{energy-product}`` is replaced by the name of the energy product being distributed (e.g., ``electricity``, ``fuelwood``, ``dh``, etc.).

Additional arguments
============================


The module supports several options to customize the distribution process. The available options are summarized in the table below:

.. csv-table:: Geographical distribution overview
   :file: ../tables/ebmgeodist_command_options.csv
   :header-rows: 1

.. note::

    The double dashes ``--`` before each option are required when running the module from the command line. In the table above the double dashes 
    are omitted for better readability. For more detailed information about each option, you can run:

    .. code-block:: bash

      python -m ebmgeodist --help
    The option ``local`` means that the module will be using electricity consumption data loaded from |elhub_aggregated_data_ref| under |input_directory| to generate the distribution keys for electricity.
    
    The option ``azure`` means that the module will be using Elhub API to fetch electricity consumption data from Azure Blob Storage to generate the distribution keys for electricity.
    
    For all other energy products, the distribution keys are always loaded from the input files under the |input_directory| folder.

The general syntax for running the module with specific options is as follows:

.. code-block:: python
  
  python -m ebmgeodist <--option> 


.. tip::
    
    The options in the table can be combined. For example, to distribute bioenergy (fuelwood) consumption for residential buildings at the municipality level
    for all years, you can run:
    
    .. code-block:: bash

       python -m ebmgeodist --energy-product fuelwood --building-category residential --years 2022 2023 2024


.. seealso::

   :ref:`Geographical distribution<geo_distribution_comprehensive_doc>`
        For a more detailed description of the geographical distribution module, including input file formats and examples.

