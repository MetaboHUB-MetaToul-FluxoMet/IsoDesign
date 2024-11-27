Tutorial
========
This tutorial will guide you through the main steps of IsoDesign, from the input of a metabolic network model to the analysis of simulation results.


Upload data
------------------------

Required input data files
~~~~~~~~~~~~~~~~~~~~~~~~~

IsoDesign uses a specific file format, introduced in influx_si, to describe metabolic network models: the Multiple TSV File (MTF) format.  
MTF files are tab-separated files (TSV), each with a specific role in model characterization. Each file is identified by a distinct suffix
indicating the type of information it contains. For more details on these files, please refer to the `influx_si software documentation 
<https://influx-si.readthedocs.io/en/latest/manual.html#>`_. 

IsoDesign uses a network file (with the “.netw” extension) as input. After submitting the input file, all associated MTF format files sharing 
the same model name are automatically loaded. A new section, "Network Analysis", then appears, presenting multiple tabs for exploration.  

The network analysis section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each tab provides specific information related to the model and its contents:

:Label input: displays the substrates to be used for labeling simulations.
:Isotopic measurements: displays the contents of the “.miso” file, which includes isotopic measurements that can be analyzed using mass spectrometry and/or NMR, along with the associated standard deviations (SDs).
:Inputs/Outputs: describes all input, intermediate and output metabolites.
:Fluxes: shows the initial metabolic flux values extracted from the “.tvar” file.
:Network: presents a table listing the biochemical reactions, their names, and the metabolic pathways they belong to (if specified in the ".netw" file).

After the model is successfully loaded, proceed to the next page to define the isotopic composition of the substrates.


Labels input
------------------------

Configure isotopic composition 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section allows you to configure the labeling parameters, including the proportion values, intervals, and, if desired, isotopic form prices for the substrates.

.. image:: _static/substrate_configuration.JPG
   :scale: 60%

The left-hand side lets you add forms for each substrate. Added forms are displayed in the "Configured labels input" section on the right. 

By default, the unlabeled form of the substrate is represented. The **Lower bound** and **Upper bound** fields are set to 100, and the **Number of intervals** 
fiels is set to 10. In addition, an unlabeled form is automatically added for each substrate. 

.. note:: If the lower and upper bounds are equal, the step size is ignored, and the proportion is fixed at a single value
   (e.g. if both fields are set to 100, the form will be fixed at 100% and will not be divided into intervals).


.. note:: It is recommended to keep this unlabeled form in its default configuration, as it compensates for the remaining proportions. This 
   ensures that, when combining different forms, the total of all added forms is equal to 100%.


You can define the desired labeling positions by entering a combination of 0 (unlabeled) and 1 (labeled). Additionally, you can set the lower and upper bounds 
(ranging from 0 to 100) and specify the desired number of intervals. Once the number of intervals is entered, the corresponding step size will be automatically 
calculated and displayed as a reference. You can also assign a price to each form, which will later be factored into the scoring criteria.
To add a substrate, click the "Add" button.

.. warning:: Each substrate must have at least one form added. If only one form is required, its proportion must be set to 100%.

Combination table
~~~~~~~~~~~~~~~~~~



Simulations options
------------------------

Results
------------------------

Outputs
------------------------