.. IsoDesign documentation master file, created by
   sphinx-quickstart on Mon Nov 18 10:19:08 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to IsoDesign documentation !
====================================

IsoDesign is a scientific tool selecting the optimal isotopic composition of
labeled substrates in :sup:`13`\C fluxomic labeling experiments.

Intracellular fluxes and associated statistics are estimated using the
`influx_si
software <https://influx-si.readthedocs.io/en/latest/index.html>`_.

**IsoDesign includes the following features:**

   * **Estimate from a given network and set of possible isotopic measurements**
     **the optimal isotopic composition of labeled substrates for increased**
     **flux precision**
   * **Design for both (isotopic) stationary and non-stationary fluxomics**
     **experiments**
   * Test **multiple labelled molecules**
   * **Multiple scoring criteria** to finely analyse individual, pathway and
     network level flux precisions
   * Can handle large numbers of combinations of isotopic forms of
     substrates with high performance
   * Shipped as a  pyton package and a interactive streamlit application
   * **Open-source, free and easy to install** everywhere where Python 3 runs

Built as a collaboration between the `Mathematics cell <https://www
.toulouse-biotechnology-institute
.fr/en/plateformes-plateaux/cellule-mathematiques/>`_, the
`MetaboHUB-MetaToul platform <https://mth-metatoul.com/>`_ and the `MetaSys
team <https://www.toulouse-biotechnology-institute
.fr/poles/equipe-metasys/>`_ of the Toulouse Biotechnology Institue.

The code is open-source, and available on `GitHub <https://github
.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/>`_ under a
:ref:`GPLv3 license <license>`.

This documentation is available on Read the Docs (`https://isodesign
.readthedocs.io <https://isodesign.readthedocs.io/>`_)
and can be downloaded as a `PDF file <https://readthedocs
.org/projects/isodesign/downloads/pdf/latest/>`_.

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
