Installation
============

Requirements
-----------------

IsoDesign runs on all platforms (Windows, MacOS and Linux) and requires Python (3.10 or higher) and R (3.4.0 or higher).
If you do not have a Python environment configured on your computer, we recommend that you follow the instructions
from `Anaconda <https://www.anaconda.com/download/>`_.


Installation with conda (recommended)
-------------------------

This is the recommended installation procedure. If you have a version of conda (such as miniconda or Anaconda), you can install IsoDesign with the following command:

.. code-block:: bash

    conda install isodesign -c bioconda

This will install IsoDesign and all its dependencies.


Installation with pip
-------------------------

If you don't have any version of conda (neither miniconda nor Anaconda) but do have Python3 and R 
installed on your system, you can install IsoDesign with pip.


.. code-block:: bash

    pip install isodesign

This will install IsoDesign and most of its dependencies. To use IsoDesign,
you will need some additional R dependencies (necessary for the flux
simulation part with influx_si). Once you installed IsoDesign, you can
install these dependencies by running the following command:

.. code-block:: bash

    influx_s --install_rdep

For more information on the installation of R dependencies, please refer to the
`influx_si documentation <https://influx-si.readthedocs.io/en/latest/install
.html#r-dependencies>`_ .


Alternatives & updates
----------------------

If you do not have permission to install software system-wide, you can
install IsoDesign into your user directory using the :samp:`--user` flag:

.. code-block::

    pip install --user isodesign

This does not require any special privileges.

Once the package is installed, you can update it using pip with the following
command:

.. code-block::

    pip install -U isodesign

and using conda:

.. code-block::

    conda update isodesign

Alternatively, you can also download all sources in a tarball from `GitHub
<https://github.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/>`_, but it will
be more difficult to update IsoDesign later on.
