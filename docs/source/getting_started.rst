===============
Getting started
===============
This page is a quick guide to get you started with the Energibruksmodell (EBM) framework. The framework is designed to calculate energy use in buildings. The framework is developed by the Norwegian Water Resources and Energy Directorate (NVE).

Installation
------------

To install the framework, run:

.. code-block:: bash
  
  python -m pip install energibruksmodell


Quick Start Guide
-----------------

Please, open your preferred terminal and follow the instructions below.


.. note::

    To figure out what EBM version you have installed, you can type ``ebm --version``
    These instructions are made for |version|, but should work for later versions as well.


Create an input directory
^^^^^^^^^^^^^^^^^^^^^^^^^

First, you need to create a directory with the necessary input files. To do this, run:

.. code-block:: bash

  ebm --create-input


The command creates a new directory called input with the default scenario for EBM in the current working directory.


Run the model
^^^^^^^^^^^^^

To run the actual model use the bare command with no options:

.. code-block:: bash

  ebm


By default the scenario is read from `input`, and the results are written to the directory `output`


.. seealso::

    Refer to the :doc:`user_guide` for an overview of more options for running ebm.



.. |date| date::

Last Updated on |date|.

Version: |version|.

