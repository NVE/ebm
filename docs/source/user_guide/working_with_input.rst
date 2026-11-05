.. |user_case_tek30| replace:: ``📁user-case-tek30``


Working with input
==================

EBM supports scenario-based modeling by allowing users to create and manage separate input directories. This enables
flexible experimentation with different assumptions and configurations.


Creating an input directory for a scenario
------------------------------------------

To create a new scenario in EBM, open your preferred terminal and run the following command:

.. code-block:: bash

   ebm --create-input --input=user-case-tek30


The input directory will be created using the path defined by the ``--input`` option. In this case the new input files will be
created as the subdirectory |user_case_tek30| in the current working directory.

If the directory you name does not exist, the program will attempt to create it. All input files necessary to run ebm
will be created, with their default values, in the supplied path.


.. tip::

    You can choose any valid directory name, but it is a good idea to limit to letters, numbers, and underscore. Avoid using space.


Using the input directory
-------------------------

Once the input directory is ready, you can run the model using:

.. code-block:: bash

   ebm --input=user-case-tek30

The model result as defined in |user_case_tek30| will be written to the subdirectory |output_directory|.

.. seealso::

   :ref:`Results<result files>`


.. |date| date::

Last Updated on |date|

Version: |version|.
