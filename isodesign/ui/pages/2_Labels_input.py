import streamlit as st
from sess_i.base.main import SessI
import pandas as pd

session = SessI(
        session_state=st.session_state,
        page="2_Labels_input.py")

# Retrieving substrates names from sessI
process_object = session.object_space["process_object"]

def get_carbon_length(substrate):
    """
    Obtain the carbon number of the substrate. 
    This number is retrieved from the netan dictionary (Process class). 

    :param substrate: substrate name  
    """
    carbon_length = process_object.netan["Clen"]
    if substrate in carbon_length:
        return carbon_length[substrate]

def display_linp_dataframes(data):
        """
        Displays the dataframes (dataframe of all linp configurations, 
        dataframe of linp configurations to be removed) present in 
        the page in a user-friendly way for easy reading. 

        :return: a dataframe with the linp file configurations
        """

        df = pd.DataFrame(data, 
                            columns=["Specie", "Isotopomer", "Value", "Price"],
                            index=[f"{index:03d}" for index in range(1, len(data) + 1)])
        return df
        
def remove_rows(indexes : list):
    """
    Function for deleting undisired rows (i.e. linp file configuration) 
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
    """
    # Register the widget status
    session.register_widgets({"reintegrate_combination": True})
    # Use the reintegrate_linp_configuration method in process_object,
    # which reintegrates these linp file configurations 
    process_object.reintegrate_linp_configuration(indexes)

st.set_page_config(page_title="IsoDesign", layout="wide")
st.title("Labels input")

if not process_object:
    # Display a warning message if the metabolic network model is not loaded
    st.warning("Please load a metabolic network model.")

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
                # If the isotopomers attribute is empty, the unmarked form is configured
                if not process_object.isotopomers:
                    process_object.configure_unmarked_form()
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
                                            help="Price of the substrate")

                    lb, ub, nb_intervals = st.columns(3, gap="medium")
                    with lb:
                        lower_b = st.text_input("Lower bound", 
                                                key=f"lb_{substrate_name}", 
                                                value=100)
                    with ub:
                        upper_b = st.text_input("Upper bound", 
                                                key=f"ub_{substrate_name}", 
                                                value=100)
                    with nb_intervals:
                        nb_intervals = st.text_input("Number of intervals", 
                                                    key=f"intervals_nb_{substrate_name}", 
                                                    value=100)
                    # Display the step value if the number of intervals is different from 100  
                    if int(nb_intervals) != 100:
                        st.info(f"Step = {int(upper_b)/int(nb_intervals)}")
                    
                    # When the add button is clicked, the isotopomer is added via the add_isotopomer method from the process class
                    add = st.button("Add", 
                                    key=f"add_{substrate_name}")
                    if add:
                        try:
                            process_object.add_isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b), float(price) if price else None)
                            st.toast(f"Isotopomer added in {substrate_name}")
                        except ValueError as e:
                            st.error(f"An error occurred: {e}")
            
            submit = st.button("Submit",
                            key="submit_button")

        with configured_substrates:
            st.header("Configured labels input")
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
        process_object.generate_combinations()
        process_object.configure_linp_files()
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
            simulation_button = st.button("Submit for simulations", key="simulation_button")
            session.register_widgets({"simulation_button": simulation_button})

    # If the show_combinations button is clicked, the combinations are displayed in a dataframe
    if session.widget_space["show_combinations"]:

        df_combinations=st.dataframe(display_linp_dataframes(process_object.linp_dataframes), 
                    hide_index=False, 
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="multi-row",
                    key="df_combinations")
        
        remove_combination = st.button("Remove selected combination",
                                on_click=remove_rows,
                                args=[df_combinations.selection.rows],
                                key="remove_combination")
       
    # If the remove_combination button is clicked, the selected combinations to remove are displayed in a dataframe
        if process_object.linp_to_remove:
            st.header("Removed combinations") 
            df_unused_combs = st.dataframe(display_linp_dataframes(process_object.linp_to_remove), 
                        hide_index=True, 
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="multi-row")

            reintegrate_combination = st.button("Reintegrate selected combination",
                                            on_click=reintegrate_rows,
                                            args=[df_unused_combs.selection.rows],
                                            key="reintegrate_combination")
    # If the simulation_button is clicked, the linp files are generated and the user is redirected to the simulation options page
    if session.widget_space["simulation_button"]:  
        process_object.generate_linp_files()    
        process_object.generate_vmtf_file()
        process_object.copy_files()

        process_object.save_process_to_file()

        st.switch_page(r"pages/3_Simulation_options.py")