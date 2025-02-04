Tutorial
========
This tutorial will guide you through the main steps of IsoDesign, from loading a flux model to visualizing and interpretating design results.

Load input data
------------------------

.. _required_input_data_files:

Required input data files
~~~~~~~~~~~~~~~~~~~~~~~~~

IsoDesign uses a specific file format for isotopic models of metabolic networks, introduced in `influx_si <https://influx-si.readthedocs.io/en/latest/>`_, the :file:`Multiple TSV File` (MTF) format.  
MTF files are tab-separated files (TSV), each with a specific content (list of reactions, isotopic measurements, etc). Each file is identified by a specific suffix
indicating the type of information it contains. For more details on these files, please refer to the `influx_si software documentation 
<https://influx-si.readthedocs.io/en/latest/manual.html#>`_. 

IsoDesign uses as main file a network file (with the :file:`.netw` extension) as input. After selecting the input file, all associated MTF files sharing 
the same prefix are automatically detected and loaded. A new section, "Network Analysis", then appears, presenting multiple tabs to explore the model.  

Network analysis section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each tab provides specific information related to the isotopic model:

:Label input: list the metabolite(s) defined as substrate(s) (i.e., the label input(s) of the network).
:Isotopic measurements: isotopic measurements that can be accessed by mass spectrometry and/or NMR, along with the associated standard deviations (SDs) (contained in the :file:`.miso` file).
:Inputs/Outputs: list all input, intermediate and output metabolites.
:Fluxes: initial metabolic flux values extracted from the :file:`.tvar` file.
:Network: list all reactions present in the network, with the metabolic pathways they belong to (if specified in the :file:`.netw` file).

After a model is successfully loaded, go to the next page to define the isotopic forms of the substrate(s) to be consider for experimental design.

.. _labels_input:
Define label inputs
------------------------

Define isotopic forms 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section allows you to configure the labeling parameters, including the proportions, and, if desired, the price of all isotopic forms of the substrate(s) to consider when designing the experiment.

.. image:: _static/substrate_configuration.JPG

The left-hand side lets you add forms for each substrate. Added forms are displayed in the "Configured labels input" section on the right. 

By default, only the unlabeled form of each substrate is defined. The **Lower bound** and **Upper bound** fields are set to 100, and the **Number of intervals** 
fiels is set to 10. 

.. note:: If the lower and upper bounds are equal, the step size is ignored, and the proportion is fixed at the given value
   (e.g. if both fields are set to 100, the form will be fixed at 100%).


.. note:: We recommended to keep the unlabeled form in its default configuration, as it compensates for the remaining proportions. This 
   ensures that, when combining different isotopic forms, the total of all added forms is always equal to 100%.


You can define additional isotopic forms by entering a combination of 0 (unlabeled) and 1 (labeled). Additionally, you can set the lower and upper bounds 
(ranging from 0 to 100 by default) and specify the desired number of intervals. Once the number of intervals is entered, the corresponding step size will be automatically 
calculated and displayed as a reference. You can also assign a price to each form, which can later be considered in the scoring step.
To add an isotopic form, click on the "Add" button. You can submit the forms provided to generate all combinations of label input by clicking the "Submit" button.

.. warning:: Each substrate must have at least one isotopic form defined. If only one form is required, its proportion must be set to 100%.

Generate all combinations of isotopic forms used as label input
~~~~~~~~~~~~~~~~~~
The total number of label inputs to be tested is displayed. Each combinations can be viewed in a table by clicking the "Show combinations" button. 
The table contains the following columns:

   * **ID** : combination ID,
   * **Specie** : substrate name,
   * **Isotopomer** : isotopic form of each substrate,
   * **Value** : proportion of each isotopic form,
   * **Price** : price of each isotopic form (depending on the proportion value).

To exclude one or several combinations from the design process, select the forms to exclude and click the “Remove selected combinations” button.

Then, click the “Submit for simulations” button to navigate to the “Simulation Options” page and run the calculations.


.. _simulation_options:
Run calculations
------------------------
This page enables you to configure calculations settings and run simulations using `influx_si <https://influx-si.readthedocs.io/en/latest/>`_. You can choose the desired influx_si mode 
for simulations: 

      * **influx_s** (stationary experiments) 
      * **influx_i** (instationary experiments)

Depending on the selected mode, default options are pre-selected. You can remove these options if needed or add new ones manually in the “Add option” field.
For detailed information on available options, consult the `influx_si documentation <https://influx-si.readthedocs.io/en/latest/>`_.
The page displays the total number of label inputs considered and the command that will be executed in influx_si.

.. note:: 
   When adding an option manually, enter the option name with the :samp:`--` prefix (e.g., use “--fullsys” and not “fullsys”). 


Two buttons are available:
   * **Start simulation** to launches the simulations.
   * **Interrupt simulation** to stops the simulations. 

Once the simulations is complete, you will be redirected to the next page, “Results”.

.. _results:
Results
------------------------
Results visualization
~~~~~~~~~~~~~~~~~~~~~
The raw simulation results are displayed in a table with the following columns:
   * **Name** : flux names, 
   * **Kind** : types (NET, XCH, METAB),
   * **Initial flux value** : initial flux values (from the "Value" column in :file:`.tvar` file),
   * **Value** : flux values used for simulations,
   * **Value difference** : difference between the initial and simulated flux values,
   * **ID..**. : Flux standard deviation for a given label input.

To filter the table, click on "Apply a filter". The table can be filtered based on the following criteria:
   * Flux : flux names
   * Kind : flux types (NET, XCH, METAB)
   * Pathway : metabolic pathways (if specified in the :file:`.netw` file)

.. note:: 
   To view the isotopic composition within the IDs, a file is generated in the output directory. This file is named as the main 
   model file with the suffix :file:`_files_combinations.txt.`. For more details, refer to the :ref:`outputs` section.

Scoring criteria 
~~~~~~~~~~~~~~~~~~~~~

The section below the table allows you to apply criteria and visualize the generated scores. This is the key page to **support interpretation and rank the substrates based on the biological question to be addressed**. 

.. image:: _static/scoring_criteria.JPG

The left-hand side is used to select the criteria and configure their parameters. Four general scoring criteria are available:
   * **Sum of SDs** : total sum of SDs (standard deviations) of all or a specific fluxes for each label input.
   * **Number of fluxes with SDs < threshold** : number of fluxes with SDs below a threshold (provided as parameter).
   * **Number of labeled inputs** : number of isotopic forms in label inputs.
   * **Price** : total price for each label input.

You can apply criteria individually, or combine them using mathematical operations (addition, multiplication and division, with weights assigned to each criterion). 

The right-hand side displays the generated scores as you select and configure criteria. Scores are presented both in a table and as 
a bar plot.  

By default, the bar plot displays all results from the score table. To display only specific results on the bar plot, select 
the corresponding rows in the table. The bar plot will then update to show only the selected data.
It is possible to apply a log transformation by selecting the 'Log scale' checkbox, which applies a base-10 logarithm.

Clicking the “New Score” button creates a new, independent block. This allows you to apply different scoring criteria to a separate 
dataset or explore alternative scoring configurations without affecting the previous scoring.

To export the results, click the “Export” button. The table, the generated scores table, and the bar plot will be exported in their current state 
to the output directory.

.. _outputs:
Outputs
------------------------

During the use of IsoDesign, various files are generated in the output directory:
   * :file:`[Model name].pkl` : a pickle file containing the current state of the process.
   * :file:`[Model Name]_files_combinations.txt` : a file that maps combination IDs to their corresponding isotopic compositions.
   * :file:`[Model Name]_summary.xlsx` : an Excel file containing all simulation results

In addition, a temporary folder (e.g. [model name].tmp) is created in the output directory:
   * :file:`MTF` files : all model MTF files.
   * :file:`..._res` folder : contains all output files generated by influx_si during calculations (for more details, refer to `influx_si documentation <https://influx-si.readthedocs.io/en/latest/manual.html#output-format>`_)
   * :file:`.linp` extension files : MTF format files containing the various isotopic forms and their fractions (for more details, refer to `influx_si documentation <https://influx-si.readthedocs.io/en/latest/manual.html#linp>`_)
   * :file:`.tvar.def` file : generated by influx_si during calculations.
   * :file:`.log` file : run log file containing information on how the run went.

