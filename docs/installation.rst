Installation
============

Installation with Conda (recommended)
--------------------------------------

IsoDesign requires Python 3.10 or higher and run on all platforms supporting
Python3 (Windows, MacOS and Linux).
If you do not have a Python environment configured on your computer, we
recommend that you follow the instructions from `Anaconda <https://www
.anaconda.com/download/>`_.

If you have Anaconda or Miniconda installed on your system, installation of
IsoDesign resumes to:

.. code-block:: bash

    conda install isodesign -c bioconda

This will install IsoDesign and all of its dependencies..


Installation with pip
-------------------------

If you don't have any version of conda (neither miniconda nor Anaconda) but
do have Python3 and R installed on your system, you can install IsoDesign
with pip.


.. code-block:: bash

    pip install isodesign

This will install IsoDesign, though some dependencies may be missing. This
is due to the influx_si package, which requires R dependencies. You can
install these dependencies by running the following command:

.. code-block:: bash

    influx_s --install_rdep

For more information on the installation of R dependencies, please refer to the
`influx_si documentation <https://influx-si.readthedocs.io/en/latest/install
.html#r-dependencies>`_ .


Alternatives & updates
----------------------

If you know that you do not have permission to install software system-wide
using pip, you can install IsoDesign into your user directory using the
:samp:`--user` flag:

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
