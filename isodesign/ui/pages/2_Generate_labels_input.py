import streamlit as st
from sess_i.base.main import SessI
import pandas as pd

session = SessI(
        session_state=st.session_state,
        page="2_Generate_labels_input.py")

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

def remove_combinations():
    """
    Function for deleting combinations of labelled substrates 
    (i.e. corresponding to a line in the combination dataframe). 
    """
    # Register the widget status
    session.register_widgets({"remove_combination": True})
    # Retrieve the selected combinations from the dataframe widget 
    if df_combinations.selection.rows:
        # If the attribute df_unused_combinations is None, it is initialized with the selected combinations
        # Otherwise, the selected combinations are concatenated to the existing ones
        if process_object.df_unused_combinations is None:
            process_object.df_unused_combinations = process_object.df_combinations.iloc[df_combinations.selection.rows, :]
        else:
            process_object.df_unused_combinations = pd.concat([process_object.df_unused_combinations, process_object.df_combinations.iloc[df_combinations.selection.rows, :]])
        # The selected combinations are removed from the labelled_substrates_combinations attribute
        for index in sorted(df_combinations.selection.rows, reverse=True):
            del process_object.labelled_substrates_combs[index]
            
    

st.set_page_config(page_title="IsoDesign", layout="wide")
st.title("Labels input")

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
            # Form to configue an isotopomer for each substrate
            with st.form(f"form_{substrate_name}"):
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

                lb, ub, step = st.columns(3, gap="medium")
                with lb:
                    lower_b = st.text_input("Lower bound", key=f"lb_{substrate_name}", value=100)
                with ub:
                    upper_b = st.text_input("Upper bound", key=f"ub_{substrate_name}", value=100)
                with step:
                    nb_intervals = st.text_input("Step", key=f"step_{substrate_name}", value=100)
                # When the add button is clicked, the isotopomer is added via the add_isotopomer method from the process class  
                add = st.form_submit_button("Add")

                if add:
                    process_object.add_isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b), float(price) if price else None)
                    st.toast(f"Isotopomer added in {substrate_name}")
        
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
    process_object.generate_labelled_substrates_dfs()

# If the submit button is clicked, the user can choose to show the combinations generated or submit for simulations
if session.widget_space["submit_button"]:
    st.info(f"{len(process_object.labelled_substrates_combs)} combinations were generated.")
    show_comb, go_simulations = st.columns([1, 7])
    with show_comb:
        show_combinations = st.button("Show combinations",
                                    key="show_combinations")
        if show_combinations:
            session.register_widgets({"show_combinations": show_combinations})
    
    with go_simulations:
        simulation_button = st.button("Submit for simulations", key="simulation_button")
        session.register_widgets({"simulation_button": simulation_button})

# If the show_combinations button is clicked, the combinations are displayed in a dataframe
if session.widget_space["show_combinations"]:
    df_combinations=st.dataframe(process_object.show_combinations(), 
                hide_index=True, 
                use_container_width=True,
                on_select="rerun",
                selection_mode="multi-row",
                key="df_combinations")
    
    remove_combination = st.button("Remove selected combinations",
                            on_click=remove_combinations,
                            key="remove_combination",
                            disabled=True if not df_combinations.selection.rows else False)
                            
# If the remove_combination button is clicked, the selected combinations to remove are displayed in a dataframe
if session.widget_space["remove_combination"]:
    st.header("Removed combinations") 
    df_unused_combs = st.dataframe(process_object.df_unused_combinations, 
                hide_index=True, 
                use_container_width=True,
                on_select="rerun",
                selection_mode="multi-row")

# If the simulation_button is clicked, the linp files are generated and the user is redirected to the simulation options page
if session.widget_space["simulation_button"]:  
    process_object.generate_linp_files()    
    process_object.generate_vmtf_file()
    process_object.copy_files()

    process_object.save_process_to_file()

    st.switch_page(r"pages/3_Simulation_options.py")
