import streamlit as st
from sess_i.base.main import SessI


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


st.set_page_config(page_title="IsoDesign", layout="wide")
st.title("Generate labels input")

# Add a space between page title and content 
st.write(" ")

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
                nb_intervals = st.text_input("Nb intervals", key=f"step_{substrate_name}", value=100)
            # When the add button is clicked, the isotopomer is added via the add_isotopomer method from the process class  
            add = st.form_submit_button("Add")

            if add:
                process_object.add_isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b), float(price) if price else None)
                st.toast(f"Isotopomer added in {substrate_name}")


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
            
                    
    submit = st.button("Submit")
    
    if submit:
        process_object.generate_combinations()
        # linp file generations 
        process_object.generate_linp_files()
        process_object.generate_vmtf_file()
        process_object.copy_files()
        process_object.save_process_to_file()
        st.switch_page(r"pages/3_Simulation_options.py")
