:orphan:
===============
Hovedoverskrift
===============

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque molestie arcu non erat vulputate faucibus.
**This text is bold**. Suspendisse tincidunt feugiat aliquet. Praesent eget felis velit. *This text is italic*
In rutrum dui eu suscipit accumsan. ``This text is monospaced`` Etiam tellus velit, tincidunt sit amet enim vitae,
consectetur egestas sapien. `Link med tekst <https://www.jeffquast.com/post/technical_writing_with_sphinx/>`_, In
consequat commodo neque in dapibus.

.. contents:: Table of Contents
   :depth: 2
   :local:


Seksjonsoverskrift 1
====================

Duis ac dignissim purus. Integer tempor sem et porttitor egestas. Interdum et malesuada fames ac ante ipsum primis in
faucibus. Proin molestie iaculis gravida. Praesent sollicitudin a enim non efficitur. Cras
euismod mi eros, cursus ornare odio accumsan eu.

Etiam quis purus in lacus molestie venenatis. Vestibulum feugiat non lorem non tristique. In nec viverra augue.



Autonummerert liste
-------------------

#. Autoummerert liste punk 1
#. Autoummerert liste punk 2
#. Autoummerert liste punk 3


Unummerert liste
----------------
 * `Technical writing with sphinx <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html/>`_
 * `How should I mark up lists? <https://docutils.sourceforge.io/FAQ.html#how-should-i-mark-up-lists/>`_
 * Punkt 3


Tekstendringer
==============

Forskjellige eksempler
----------------------

- **This text is bold**
- *This text is italic*
- ``This text is monospaced``
- ``inline code``
- :sub:`subscript text`
- :sup:`superscript text`
- kvadratmeter: m\ :sup:`2`


Ordbryting
----------

For å fortelle sphinx hvor man vil dele veldig lange ord kan man bruke unicode-tegnet U+00AD for myk bindestrek (`Soft Hypen <https://en.wikipedia.org/wiki/Soft_hyphen>`_) forkortet til SHY.

Hvordan skrive SHY med Windows?
    Holde nede venstre [ALT] og tast inn 0173 med de numeriske tastene til høyre på tastaturet.

Ordet AAA…AAA har SHY
^^^^^^^^^^^^^^^^^^^^^

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA­AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA­AAAAAAAAAAAAAA


Ordet BBB…BBB mangler SHY
^^^^^^^^^^^^^^^^^^^^^^^^^
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB



Bilde 🖼️
========

.. image:: _static/kjetil_lund.jpg
   :alt: Kjetil Lund, Director General of NVE
   :width: 300px
   :align: center


Tabeller
========

.. container:: boxed

   Legg merge til tomme linjer og innrykk (2 space).


Tabell med tekst «simple»
-------------------------


.. table::

  =====  =====  =======
  A      B      A and B
  =====  =====  =======
  False  False  False
  True   False  False
  False  True   False
  True   True   True
  =====  =====  =======


Tabell med tekst
----------------

Legge merke til tommelinjer og innrykk ➡️➡️. Bruken av mellomrom må være konsekvent.

⬇️ Det er tom linje mellom denne paragrafen og ``.. table::``

.. table::

  +------------------------+------------+----------+----------+
  | Header row, column 1   | Header 2   | Header 3 | Header 4 |
  | (header rows optional) |            |          |          |
  +========================+============+==========+==========+
  | body row 1, column 1   | column 2   | column 3 | column 4 |
  +------------------------+------------+----------+----------+
  | body row 2             | ...        | ...      |          |
  +------------------------+------------+----------+----------+

⬆️ Det er tom linje mellom denne paragrafen og siste innhold i tabellen ``+-- … --+``.



Inline CSV-tabell
-----------------
.. csv-table:: Construction by building category and TEK

   :header: building_category,TEK,area
    building_category,TEK,area
    apartment_block,PRE_TEK49_RES_1950,11444245
    apartment_block,TEK49_RES,7133096
    apartment_block,TEK69_RES_1976,6739001


CSV-tabell fra fil
------------------

.. csv-table:: Construction by building category and TEK
   :file: ../../ebm/data/construction_building_category_yearly.csv
   :header-rows: 1



Inline CSV-tabell
-----------------
.. csv-table:: Construction by building category and TEK

   :header: building_category,TEK,area
    building_category,TEK,area
    apartment_block,PRE_TEK49_RES_1950,11444245
    apartment_block,TEK49_RES,7133096
    apartment_block,TEK69_RES_1976,6739001


CSV-tabell fra fil
------------------

.. csv-table:: Construction by building category and TEK
   :file: ../../ebm/data/construction_building_category_yearly.csv
   :header-rows: 1



Definisjonsliste
================


term 1
    Definition 1.

term 2
    Definition 2, paragraph 1.

    Definition 2, paragraph 2.

term 3 : classifier
    Definition 3.

term 4 : classifier one : classifier two
    Definition 4.

\-term 5
    Without escaping, this would be an option list item.


Kode-eksempel
==============

python 🐍
------
.. code-block:: python

   from ebm.model.data_classes import YearRange
   from ebm.model.database_manager import DatabaseManager
   from ebm.model.energy_requirement import EnergyRequirement

   dm = DatabaseManager()
   energy_requirements = EnergyRequirement.new_instance(period=YearRange(2020, 2050),
                                                        calibration_year=2020,
                                                        database_manager=dm)
   df =  energy_requirements.calculate_energy_requirements()

   print(df)

powershell 🐚
----------

.. code-block:: powershell

   Measure-Command { python -m ebm } | Select-Object -ExpandProperty TotalSeconds

Diverse
=======

tegn for overskrift
-------------------

.. code-block:: text

   # with overline, for parts 1
   * with overline, for chapters 2
   =, for sections 3
   -, for subsections 4
   ^, for subsubsections 5
   ", for paragraphs 6
