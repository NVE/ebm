Geographical_distribution
=========================

To use the geographical distribution module ``ebmgeodist``, you can follow the instructions below.

Quick Start Guide
-----------------

Please, open your preferred terminal and follow the instructions below.


Create an input directory
^^^^^^^^^^^^^^^^^^^^^^^^^

First, you need to create the necessary input files. To do this, run:

.. code-block:: bash

  python -m ebmgeodist --create-input

The command creates the necessary input files in a new directory called `input` in the current working directory.

To run the actual geographical distribution module, it is sufficient to use the bare command with no options:

.. code-block:: bash

  python -m ebmgeodist

By default, the distribution keys are loaded from `input`, and the results are written to the directory `output`.
Running the module without any options will distribute electricity consumption use for all building categories at the municipality level.
By default, the distribution keys are loaded from the input file ``yearly_aggregated_elhub_data.parquet`` under the ``input`` folder.
If the file does not exist, the module will generate the distribution keys using Elhub API inside the module, assuming that the user
has access to Elhub data via Azure Blob Storage. 

The results are saved in an Excel file named ``ebmgeodist_output.xlsx`` under the ``output`` folder.

Additional arguments
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python
  
  python -m ebmgeodist <--switch> <step> <output filename>


