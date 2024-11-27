.. IsoDesign documentation master file, created by
   sphinx-quickstart on Mon Nov 18 10:19:08 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to IsoDesign documentation !
=======================

IsoDesign is a scientific tool designed to optimize the choice of the optimal 
isotopic composition of labeled substrates in 13C fluxomic labeling experiments.

Simulated labeling is calculated using the `influx_si software <https://influx-si.readthedocs.io/en/latest/index.html>`_ , distributed with IsoDesign. 

**IsoDesign includes the following features:**

   * user can **define lower and upper bounds** (between 0 and 100) and **define the desired number of intervals** for each isotopic form to be included,
   * **substrate pricing can be entered**, which will be incorporated into the rating criteria,
   * **simulation of all possible combinations** of isotopic forms in a single run,
   * ability to **simulate stationary or instationary labeling**, 
   * **multiple scoring criteria** are available and can be applied simultaneously to assess simulation results,
   * the results of the scoring criteria are displayed using a table for detailed values and a bar plot for visual representation,
   * shipped as a **library** with a **graphical** interface,
   * **open-source, free and easy to install** everywhere where Python 3 and pip run,
   * **biologist-friendly**.

It is one of the routine tools that we use at the
`Mathematics cell of TBI <https://www.toulouse-biotechnology-institute.fr/en/plateformes-plateaux/cellule-mathematiques/>`_
and `MetaToul platform <https://mth-metatoul.com/>`_ .

The code is open-source, and available on `GitHub <https://github.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/>`_ under a
:ref:`GPLv3 license <license>` .

This documentation is available on Read the Docs (`https://isodesign.readthedocs.io <https://isodesign.readthedocs.io/>`_)
and can be downloaded as a `PDF file <https://readthedocs.org/projects/isodesign/downloads/pdf/latest/>`_.

.. toctree::
   :maxdepth: 2
   :caption: User documentation

   installation.rst
   quickstart.rst
   tutorial.rst


.. toctree::
   :maxdepth: 2
   :caption: Miscellaneous

   license.rst
   