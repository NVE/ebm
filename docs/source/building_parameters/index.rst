.. _building_category_building_code_doc:

Building categories and building codes
======================================

The tables below show the different building categories and building codes (TEK) 
which are used in the model. The building category table shows what types of buildings are included under the
main building category. The building categories are the same as defined in the building code except for “light industry and repairs”. 
From this category the model only uses the area attributed to storage and warehouses, and the category is then named “storage”.

.. csv-table:: Building categories and associated building types
  :file: ../tables\building_category.csv
  :header-rows: 1
  :widths: 25 25
  :delim: ;

For already built area we assume that all area in a given building code is built the same year. This year is "building year" in the table below. 

.. csv-table:: Building codes and their active years
  :file: ../tables\building_code_parameters.csv
  :header-rows: 1
  :widths: 25 25 25 25
  :delim: ,


.. |date| date::

Last Updated on |date|

Version: |version|.
