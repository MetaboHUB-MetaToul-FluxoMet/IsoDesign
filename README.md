# IsoDesign

## What is IsoDesign ?
IsoDesign is a scientific tool designed to optimize the choice of the optimal 
isotopic composition of labeled substrates in 13C fluxomic labelling experiments. Simulated labeling is calculated using the [*influx_si* software](https://influx-si.readthedocs.io/en/latest/index.html), distributed with IsoDesign. 

It is one of the routine tools that we use at the [Mathematics cell of TBI](https://www.toulouse-biotechnology-institute.fr/en/plateformes-plateaux/cellule-mathematiques/) 
and [MetaToul platform](https://www.metabohub.fr/home.html) in functional studies of metabolic systems.

Detailed documentation can be found online at Read the Docs ().

## Key features

   * user can **define lower and upper bounds** (between 0 and 100) and **define the desired number of intervals** for each isotopic form to be included,
   * **substrate pricing can be entered**, which will be incorporated into the scoring criteria,
   * **simulation of all possible combinations** of isotopic forms in a single run,
   * ability to **simulate stationary or instationary labeling**, 
   * **multiple scoring criteria** are available and can be applied simultaneously to assess simulation results,
   * the results of the scoring criteria are displayed using a table for detailed values and a bar plot for visual representation,
   * shipped as a **library** with a **graphical** interface,
   * **open-source, free and easy to install** everywhere where Python 3 and pip run,
   * **biologist-friendly**.


## Quick-start

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
In development mode, do a `pip install -e /path/to/IsoDesign` to install
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


