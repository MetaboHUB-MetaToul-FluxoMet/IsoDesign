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
   * can be applied to both **stationary** and **instationary** :sup:`13`\ **C-flux experiments**, 
   * account for the **substrate price** to keep the cost of the experiment reasonable,
   * **several scoring criteria** can be applied to identify the optimal label input according to the biological question to be addressed,
   * **scoring criteria can be combined** to find the optimal balance between different objectives (e.g., the highest flux resolution at a minimal cost),
   * **visual representation** of the design results to support the decision-making process,
   * shipped as a **library** with a **graphical user interface**,
   * **open-source, free and easy to install** everywhere where Python and R run,
   * **biologist-friendly**.

It is one of the routine tools that we use at the `MetaToul platform <https://mth-metatoul.com/>`_ and 
`MetaSys team <http://www.toulouse-biotechnology-institute.fr/en/research/molecular-physiology-and-metabolism/metasys.html>`_ of the `Toulouse Biotechnology Institute <http://www.toulouse-biotechnology-institute.fr/en/>`_.
IsoDesign has been developed in collaboration with the `Math cell of TBI <https://www.toulouse-biotechnology-institute.fr/en/plateformes-plateaux/cellule-mathematiques/>`_, with the continuous support of `MetaboHUB <https://www.metabohub.fr/home.html>`_.

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