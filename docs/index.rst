.. IsoDesign documentation master file, created by
   sphinx-quickstart on Fri Jan 31 09:51:42 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IsoDesign documentation !
=======================

IsoDesign is a scientific tool designed to identify the optimal 
isotopic composition of labeled substrates in :sup:`13`\ C-fluxomics experiments.

**Key features:**

   * user can **define the isotopic forms to consider of each substrate**,
   * can be applied to **stationary or instationary** :sup:`13`\ **C-flux experiments**, 
   * account for the **substrate price** to keep reasonable the cost of the experiment,
   * **several scoring criteria** can be applied to identify the optimal label input according to the biological question to be addressed,
   * **combination of different scoring criteria** is possible,
   * shipped as a **library** with a **graphical** interface,
   * **open-source, free and easy to install** everywhere where Python 3 and pip run,
   * **biologist-friendly**.

It is one of the routine tools that we use at the `MetaToul platform <https://mth-metatoul.com/>`_ and 
`MetaSys team <http://www.toulouse-biotechnology-institute.fr/en/research/molecular-physiology-and-metabolism/metasys.html>`_ of `Toulouse Biotechnology Institute <http://www.toulouse-biotechnology-institute.fr/en/>`_.

The code is open-source, and available on `GitHub <https://github.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/>`_ under a
:ref:`GPLv3 license <license>`.

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