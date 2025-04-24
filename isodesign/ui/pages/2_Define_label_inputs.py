import streamlit as st
from sess_i.base.main import SessI
import pandas as pd

#############
# FUNCTIONS #
#############

def get_carbon_length(substrate):
    """
    Obtain the carbon number of the substrate. 
    This number is retrieved from the netan dictionary (Process class). 

    :param substrate: substrate name  
    """
    carbon_length = process_object.netan["Clen"]
    if substrate in carbon_length:
        return carbon_length[substrate]

        
def remove_rows(indexes : list):
    """
    Function for deleting undesired rows (i.e. linp file configuration) 
    from the linp overview dataframe according to the indexes 
    selected by the user.
    """
    # Register the widget status
    session.register_widgets({"remove_combination": True})
    # Use the remove_linp_configuration method in process_object,
    # which deletes these linp file configurations 
    process_object.remove_linp_configuration(indexes)
 
def reintegrate_rows(indexes : list):
    """
    Function for reintegrating undisired rows (i.e. linp file configuration) 
    from the linp overview dataframe according to the indexes 
    selected by the user.

    :param indexes: list of indexes selected by the user
    """
    # Register the widget status
    session.register_widgets({"reintegrate_combination": True})

    # Create a list of keys to reintegrate by getting the keys from linp_to_remove
    # corresponding to the selected indexes.
    keys_to_reintegrate = [
            list(process_object.linp_to_remove.keys())[index] for index in indexes]
    # Call the reintegrate_linp_configuration method to reintegrate the selected 
    # linp DataFrames back into the linp_dataframes list.
    process_object.reintegrate_linp_configuration(keys_to_reintegrate)


########
# MAIN #
########

st.set_page_config(page_title="IsoDesign", 
                   layout="wide")
st.title("Define label inputs")

session = SessI(
        session_state=st.session_state,
        page="2_Define_label_inputs.py")

# Retrieving substrates names from sessI
process_object = session.object_space["process_object"]

if not process_object or not process_object.netan:
    # Display a warning message if the metabolic network model is not loaded
    st.warning("Please load a metabolic network model in 'Upload data' page.")
else:
    # Add a space between page title and content 
    st.write(" ")

    # Create a container to display the substrates and the configured labels input
    with st.container(border=True):
        # Create two columns to display the substrates and the configured labels input
        substrates, configured_substrates = st.columns(2, gap="large")

        with substrates:
            for substrate_name in process_object.netan["input"]:
                st.header(substrate_name)
                # If the isotopomers attribute is empty, the unlabelled form is configured
                if not process_object.isotopomers:
                    process_object.configure_unlabelled_form()
                # Container to configure an isotopomer for each substrate
                with st.container(border=True):
                    labelling, price = st.columns(2)
                    with labelling:
                        labelling = st.text_input(f"Number of tracer atoms : {get_carbon_length(substrate_name)}", 
                                            key=f"labelling_{substrate_name}", 
                                            value="0" * get_carbon_length(substrate_name))
                    
                    with price:
                        price = st.text_input("Price", 
                                            key=f"price_{substrate_name}", 
                                            value=None,
                                            help="Price of the substrate.\
                                                There's no need to add units (e.g. €, $, etc.) - just enter the numerical value.")

                    lb, ub, intervals_nb = st.columns(3, gap="medium")
                    with lb:
                        lower_b = st.text_input("Lower bound", 
                                                key=f"lb_{substrate_name}", 
                                                value=1,
                                                help="The lower and upper bounds are expressed as fractions.\
                                                    For example, a value of 1 corresponds to 100% labeling, and 0.5 corresponds to 50%.")
                    with ub:
                        upper_b = st.text_input("Upper bound", 
                                                key=f"ub_{substrate_name}", 
                                                value=1,
                                                help="The lower and upper bounds are expressed as fractions.\
                                                    For example, a value of 1 corresponds to 100% labeling, and 0.5 corresponds to 50%.")
                    with intervals_nb:
                        intervals_nb = st.text_input("Number of intervals", 
                                                    key=f"intervals_nb_{substrate_name}", 
                                                    value=10)
                    
                    # Display the step size between the lower and upper bounds  
                    if int(lower_b) != int(upper_b) :
                        st.info(f"Step = {(int(upper_b)-int(lower_b))/int(intervals_nb)}")
                    
                    # When the add button is clicked, the isotopomer is added via the add_isotopomer method from the process class
                    add = st.button("Add", 
                                    key=f"add_{substrate_name}")
                    if add:
                        try:
                            process_object.add_isotopomer(
                                substrate_name = substrate_name, 
                                labelling = labelling, 
                                intervals_nb = int(intervals_nb), 
                                lower_b = int(lower_b),
                                upper_b = int(upper_b), 
                                price = float(price) if price else None)
                            st.toast(f"Isotopomer added in {substrate_name}")
                        except ValueError as e:
                            st.error(f"An error occurred: {e}")
            
            submit = st.button("Submit",
                            key="submit_button")

        with configured_substrates:
            st.header("Configured label inputs")
            for substrate_name in process_object.isotopomers.keys():
                # Create an expander to display the isotopomers for each labels input
                with st.expander(f"{substrate_name}", expanded=True):
                    for index, isotopomer in enumerate(process_object.isotopomers[substrate_name]):
                        iso_infos, delete = st.columns([10, 1])
                        with iso_infos:
                            st.write(isotopomer)
                        with delete:
                            # When the delete button is clicked, the isotopomer is removed via the remove_isotopomer method from the process class
                            delete = st.button(label=":x:",
                                                key=f"delete_{substrate_name}_{index}",
                                                help="Delete isotopomer",
                                                on_click=process_object.remove_isotopomer,
                                                args=(isotopomer.name, isotopomer.labelling))
                    
        
    if submit:
        session.register_widgets({"submit_button": submit})
        # Generate the combinations of isotopomers
        try:
            process_object.generate_combinations()
            process_object.configure_linp_files()
        except ValueError as e:
            st.error(f"An error occurred: {e}")
        # This lines are usefull in case of a re-submission
        session.widget_space.widgets["show_combinations"] = False
        session.widget_space.widgets["remove_combination"] = False
        
   
    if process_object.linp_dataframes:
        st.info(f"{len(process_object.linp_dataframes)} combinations were generated.")
        # Creates two columns: one for displaying combinations and one for submitting simulations
        show_comb, go_simulations = st.columns([1, 7])
        with show_comb:
            # Creates a button to display combinations and saves it's state in the session
            show_combinations = st.button("Show combinations",
                                        key="show_combinations")
            if show_combinations:
                session.register_widgets({"show_combinations": show_combinations})
        
        with go_simulations:
            # Creates a button for submitting simulations and saves it's status in the session
            simulation_button = st.button("Validate inputs", key="simulation_button")
            session.register_widgets({"simulation_button": simulation_button})

    # If the show_combinations button is clicked, the combinations are displayed in a dataframe
    if session.widget_space["show_combinations"]: 
        # Display the combinations in a dataframe
        df = pd.DataFrame(process_object.linp_dataframes.values(),
                            columns=["Specie", "Isotopomer", "Value", "Price"])
        df.insert(0, "ID", process_object.linp_dataframes.keys())
        
        df_combinations=st.dataframe(df, 
                    hide_index=True, 
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="multi-row",
                    key="df_combinations")
        
        remove_combination = st.button("Remove selected combination(s)",
                                on_click=remove_rows,
                                args=[df_combinations.selection.rows],
                                key="remove_combination")
       
    # If the remove_combination button is clicked, the selected combinations to remove are displayed in a dataframe
        if process_object.linp_to_remove:
            st.header("Removed combinations") 
            # Display the removed combinations in a dataframe
            df_unused = pd.DataFrame()
            for linp_id in process_object.linp_to_remove.values():
                df = pd.DataFrame(
                    linp_id.values(),
                    columns=["Specie", "Isotopomer", "Value", "Price"]
                )
                df.insert(0, "ID", linp_id.keys())
                df_unused = pd.concat([df_unused, df])
           
            df_unused_combs = st.dataframe(df_unused, 
                        hide_index=True, 
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="multi-row")

            reintegrate_combination = st.button("Reintegrate selected combination(s)",
                                            on_click=reintegrate_rows,
                                            args=[df_unused_combs.selection.rows],
                                            key="reintegrate_combination")
    # If the simulation_button is clicked, the linp files are generated and the user is redirected to the simulation options page
    if session.widget_space["simulation_button"]:  
        process_object.clear_previous_linp()
        process_object.generate_linp_files()    
        process_object.generate_vmtf_file()
        process_object.copy_files()

        process_object.save_process_to_file()

        st.switch_page(r"pages/3_Run_simulations.py")