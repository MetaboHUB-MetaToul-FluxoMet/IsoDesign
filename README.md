# IsoDesign

[![PyPI version](https://badge.fury.io/py/isodesign.svg)](https://badge.fury.io/py/isodesign)
[![Documentation Status](https://readthedocs.org/projects/isodesign/badge/?version=latest)](https://isodesign.readthedocs.io/en/latest/?badge=latest)

## What is IsoDesign ?
IsoDesign is a scientific tool designed to identify the optimal
isotopic composition of labeled substrates in :sup:`13`\ C-fluxomics
experiments.

It is one of the routine tools that we use at the [MetaToul platform](https://mth-metatoul.com/) 
and [MetaSys team](http://www.toulouse-biotechnology-institute.fr/en/research/molecular-physiology-and-metabolism/metasys.html) of the 
[Toulouse Biotechnology Institute](http://www.toulouse-biotechnology-institute.fr/en/).
IsoDesign has been developed in collaboration with the [Math cell of TBI](https://www.toulouse-biotechnology-institute.fr/en/plateformes-plateaux/cellule-mathematiques/), with the continuous
support of [MetaboHUB](https://www.metabohub.fr/home.html).

The code is open-source, and available under a GPLv3 license.

This documentation is available on [Read the Docs](https://isodesign.readthedocs.io).

## Key features

   * users can **define all isotopic forms to consider for each substrate**,
   * account for the **substrate price** to keep the cost of the experiment
     reasonable,
   * design of both (isotopic) **stationary and non-stationary** :sup:`13`\ C-fluxomics experiments
   * **diverse scoring criteria** to finely analyse flux resolution at reaction-, pathway- and
     network-levels to identify the optimal label input
     according to the biological question,
   * **scoring criteria can be combined** to find the optimal balance
     between different objectives (e.g., the highest flux resolution at a
     minimal cost),
   * **visual representation** of the design results to support the
     decision-making process,
   * increased computational performance through **parallel computing**,
   * shipped as a **library** with a **graphical user interface**,
   * **open-source, free and easy to install** everywhere where Python and R
     run,
   * **biologist-friendly**.


## Quick-start

IsoDesign runs on all platforms and requires Python (3.10 or higher) and R (3.4.0 or higher).
Please check [the documentation](https://isodesign.readthedocs.io/en/latest/quickstart.html) for complete
installation and usage instructions.

### Installation with pip
If you have Python3 and R 
installed on your system, you can install IsoDesign from Pypi with pip :

```bash
$ pip install isodesign
```

To use IsoDesign, you will need to some R dependencies (necessary for influx_si).
Once you have installed IsoDesign, you can install these dependencies by running the following command:

```bash
$ influx_s --install_rdep
```

For more information on the installation of R dependencies, please refer to [influx_si software](https://influx-si.readthedocs.io/en/latest/install.html#r-dependencies) documentation.


Then, start the graphical interface with:

```bash
$ isodesign
```

IsoDesign is also available directly from command-line and as a Python library.


## Bug and feature requests
If you have an idea on how we could improve IsoDesign please submit a new *issue*
to [our GitHub issue tracker](https://github.com/MetaboHUB-MetaToul-FluxoMet/IsoDesign/issues).


## Developers guide
### Contributions
Contributions are very welcome! :heart:

Please work on your own fork,
follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide,
and make sure you pass all the tests before a pull request.

### Local install with pip
In development mode, do a `pip install -e /path/to/isodesign` to install
locally the development version.

### Build the documentation locally
Build the HTML documentation with:

```bash
$ cd doc
$ make html
```

The PDF documentation can be built locally by replacing `html` by `latexpdf`
in the command above. You will need a recent latex installation.

## Authors
Rochelle KOUAKOU, Loic LE GREGAM

## Contacts
:email: kouakou@insa-toulouse.fr, legregam@insa-toulouse.fr


