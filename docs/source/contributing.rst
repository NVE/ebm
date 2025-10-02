Contributing
============

Thank you for your interest in contributing to **Energibruksmodell**!
Your help is greatly appreciated. This guide outlines how you can get
involved, report issues, suggest improvements, and submit code.

About the Project
-----------------

EBM is a bottom-up model that estimates how area, energy need, heating
systems and energy use in the building stock changes over time. The
model is developed in-house by the Norwegian Water Resources- and Energy
Directorate (NVE). It is an open source model, with an accompanying
dataset developed by NVE.

EBM is written in Python.


How to Contribute
-----------------

There are many ways to contribute:

1. Report Bugs
~~~~~~~~~~~~~~

If you find a bug, please open an issue with:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)

2. Suggest Enhancements
~~~~~~~~~~~~~~~~~~~~~~~

Have an idea for a new feature or improvement? Open an issue and
describe:

- The motivation behind the suggestion
- How it would benefit users
- Any potential implementation ideas

3. Submit Code
~~~~~~~~~~~~~~

We welcome pull requests! To contribute code:

1. Fork the repository
2. Create a new branch (``feature/my-feature`` or ``bugfix/my-bug``)
3. Make your changes with clear, concise commits
4. Write or update tests if applicable
5. Ensure the code passes linting and tests
6. Submit a pull request with a detailed description

4. Improve Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

Good documentation is key! You can help by:

- Fixing typos or grammar
- Adding examples or clarifications
- Translating content (if applicable)

The documentation is written in reStructuredText and is located under the subdirectory ``docs/source``


--------------


Development Setup
-----------------

To set up the project locally:

.. code:: shell

   git clone https://github.com/nve/Energibruksmodell.git
   cd Energibruksmodell
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate.ps1 on Windows


--------------

Code Style & Guidelines
-----------------------

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Keep pull requests focused and minimal
- Include docstrings and comments where helpful

--------------


Testing with Pytest
----------------------

We use pytest for testing. All new features and bug fixes should include
relevant tests.

Running Tests
~~~~~~~~~~~~~

To run the test suite:

.. code:: shell


   pytest tests/


Writing Tests
~~~~~~~~~~~~~

- Place your tests in the ``tests/ebm`` directory.
- Name test files starting with ``test_``.
- Use descriptive names for test functions.
- Prefer fixtures for setup and teardown logic.

Example:

.. code:: python

   from ebm.model.scurve import SCurve

   def test_energy_calculation():
       s_curve = SCurve(earliest_age=5,
                        average_age=20,
                        rush_years=20,
                        last_age=50,
                        rush_share=0.8,
                        never_share=0.1)

       assert s_curve._calc_pre_rush_rate() == 0.01


--------------

License
-------

By contributing, you agree that your contributions will be licensed
under the MIT license.

--------------

Thank You
------------

Your contributions make this project better. Whether it’s a typo fix or
a major feature, **thank you** for helping improve Energibruksmodell!


--------------

.. |date| date::

Last Updated on |date|.

Version: |version|.
