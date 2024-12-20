Installation
============

Installation
-----------------

IsoDesign requires Python 3.10 or higher and run on all platforms supporting Python3 (Windows, MacOS and Linux).
If you do not have a Python environment configured on your computer, we recommend that you follow the instructions
from `Anaconda <https://www.anaconda.com/download/>`_.


Installation with pip
-------------------------

If you don't have any version of conda (neither miniconda nor Anaconda) but do have Python3 and R 
installed on your system, you can install IsoDesign with pip.


.. code-block:: bash

    pip install isodesign

This will install IsoDesign and all its dependencies. To use IsoDesign, you will need to some R dependencies (necessary for the simulation part with influx_si).
Once you installed IsoDesign, you can install these dependencies by running the following command:

.. code-block:: bashy

    influx_s --install_rdep

For more information on the installation of R dependencies, please refer to `influx_si software <https://influx-si.readthedocs.io/en/latest/install.html#r-dependencies>`_ documentation.


Alternatives & updates
----------------------

If you know that you do not have permission to install software system-wide, you can install IsoDesign into your user directory using the :samp:`--user` flag:

.. code-block::

    pip install --user isodesign

This does not require any special privileges.

Once the package is installed, you can update it using the following command:

.. code-block::

    pip install -U isodesign

Alternatively, you can also download all sources in a tarball from `GitHub <https://github.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/>`_,
but it will be more difficult to update IsoDesign later on.
