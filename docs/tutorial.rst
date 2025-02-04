Tutorial
========
This tutorial will guide you through the main steps of IsoDesign, from the input of a metabolic network model to the visualization and interpretation of simulation results.


Upload data
------------------------

.. _required_input_data_files:

Required input data files
~~~~~~~~~~~~~~~~~~~~~~~~~

IsoDesign uses a specific file format, introduced in influx_si, to describe metabolic network models: the :file:`Multiple TSV File` (MTF) format.  
MTF files are tab-separated files (TSV), each with a specific role in model characterization. Each file is identified by a distinct suffix
indicating the type of information it contains. For more details on these files, please refer to the `influx_si software documentation 
<https://influx-si.readthedocs.io/en/latest/manual.html#>`_. 

IsoDesign uses a network file (with the :file:`.netw` extension) as input. After submitting the input file, all associated MTF format files sharing 
the same model name are automatically loaded. A new section, "Network Analysis", then appears, presenting multiple tabs for exploration.  

Network analysis section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each tab provides specific information related to the model and its contents:

:Label input: displays the substrates to be used for labeling simulations.
:Isotopic measurements: displays the contents of the file with :file:`.miso` extension, which includes isotopic measurements that can be analyzed using mass spectrometry and/or NMR, along with the associated standard deviations (SDs).
:Inputs/Outputs: describes all input, intermediate and output metabolites.
:Fluxes: shows the initial metabolic flux values extracted from the file with :file:`.tvar` extension.
:Network: presents a table listing the biochemical reactions, their names, and the metabolic pathways they belong to (if specified in the :file:`.netw` file).

After the model is successfully loaded, proceed to the next page to define the isotopic composition of the substrates.

.. _labels_input:
Labels input
------------------------

Configure isotopic composition 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section allows you to configure the labeling parameters, including the proportion values, intervals, and, if desired, isotopic form prices for the substrates.

.. image:: _static/substrate_configuration.JPG

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
To add a substrate, click the "Add" button. You can submit for combinations generation by clicking the "Submit" button.

.. warning:: Each substrate must have at least one form added. If only one form is required, its proportion must be set to 100%.

Visualize the generated combinations
~~~~~~~~~~~~~~~~~~
The total number of generated combinations is displayed. Each combinations can be viewed in a table by clicking the "Show combinations" button. 
The table contains the following columns:

   * **ID** : combination ID,
   * **Specie** : substrate name,
   * **Isotopomer** : isotopic form of each substrate,
   * **Value** : proportion of each isotopic form,
   * **Price** : price of each isotopic form (depending on the proportion value).

To remove combinations, select the desired ones and click the “Remove selected combinations” button.
Click the “Submit for simulations” button to navigate to the “Simulation Options” page and start the simulations.


.. _simulation_options:
Simulation options
------------------------
This page enables you to configure simulations settings and run simulations using influx_si. You can choose the desired influx_si mode 
for simulations: 

      * **influx_s** (stationary) 
      * **influx_i** (instationary)

Depending on the selected mode, default options are pre-selected. You can remove these options if needed or add new ones manually in the “Add option” field.
For detailed information on available options, consult the influx_si documentation provided in the sidebar.
The page displays the total number of combinations to be simulated and the exact command that will be executed in influx_si.

.. note:: 
   When adding an option manually, enter the option name without including the :samp:`--` prefix (e.g., use “fullsys” instead of “--fullsys”). 


Two buttons are available:
   * **Start simulation** to launches the simulations.
   * **Interrupt simulation** to stops the simulations. 

Once the simulations is complete, you will be redirected to the next page, “Results”.

.. _results:
Results
------------------------
Results visualization
~~~~~~~~~~~~~~~~~~~~~
The simulation results are displayed in a table with the following columns:
   * **Name** : flux names, 
   * **Kind** : flux types (NET, XCH, METAB),
   * **Initial flux value** : initial flux values (from the "Value" column in :file:`.tvar` file),
   * **Value** : simulated flux values,
   * **Value difference** : difference between the initial and simulated flux values,
   * **ID..**. : Standard deviation of the simulated fluxes corresponding to a specific isotopic composition combination.

To filter the table, click on "Apply a filter". The table can be filtered based on the following criteria:
   * Flux : flux names
   * Kind : flux types (NET, XCH, METAB)
   * Pathway : metabolic pathways (if specified in the ".netw" file)

.. note:: 
   To view the isotopic composition within the IDs, a file is generated in the output directory. This file is named after 
   the model with the suffix :file:`_files_combinations.txt.`. For more details, refer to the :ref:`outputs` section.

Scoring criteria 
~~~~~~~~~~~~~~~~~~~~~

The section below the table allows you to apply criteria and visualize the generated scores. 

.. image:: _static/scoring_criteria.JPG

The left-hand side is used to select the criteria and configure their parameters. Four general scoring criteria are available:
   * **Sum of SDs** : calculated the total sum of all SDs (standard deviations) of fluxes for each isotopic composition combination.
   * **Number of fluxes with SDs < threshold** : counts the number of fluxes with SDs below a specified threshold in the parameters.
   * **Number of labeled inputs** : counts the number of labeled inputs for each isotopic composition combination.
   * **Price** : calculates the total price for each isotopic composition combination.

You can apply multiple criteria simultaneously. Additionally, mathematical operations (addition, multiplication and division) and weights
can be assigned to each criterion. 

The right-hand side displays the generated scores as you select and configure criteria. Scores are presented both in a table and as 
a bar plot.  

By default, the bar plot displays all results from the score table. To display only specific results on the bar plot, select 
the corresponding rows in the table. The bar plot will then update to show only the selected data.
It is possible to apply a log transformation by selecting the 'Apply a log' checkbox, which applies a base-10 logarithm.

Clicking the “New Score” button creates a new, independent block. This allows you to apply different scoring criteria to a separate 
dataset or explore alternative scoring configurations without affecting the existing block.

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
   * :file:`..._res` folder : contains all output files generated by influx_si during calculations (for more details, refer to the `influx_si software documentation <https://influx-si.readthedocs.io/en/latest/manual.html#output-format>`_)
   * :file:`".linp"` extension files : MTF format files containing the various isotopic forms and their fractions (for more details, refer to the `influx_si software documentation <https://influx-si.readthedocs.io/en/latest/manual.html#linp>`_)
   * :file:`MTF` files : all model MTF files.
   * :file:`".tvar.def"` file : generated by influx_si during calculations.
   * :file:`Log` file : run log file containing information on how the run went.

