import streamlit as st
from sess_i.base.main import SessI
from isodesign.base.calculation import Isotopomer


session = SessI(
        session_state=st.session_state,
        page="2_substrates_selection")

def add_substrates(substrate_name, labelling, nb_intervals, lower_b, upper_b):
    """
    Create an Isotopomer object from the substrate add

    :param substrate_name: substrate name  
    :param labelling: labelling 
    :param nb_intervals: number of intervals (step)
    :param lower_b: lower_bound
    :param upper_b: upper_bound
    """

    # Create an Isotopomer object with the given parameters
    iso = Isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b))
    if f"{substrate_name}" not in session.object_space.objects:
        # Register the Isotopomer object in the session object space with a unique key
        session.register_object([iso], key=f"{substrate_name}")
    else:
        session.object_space.objects[f"{substrate_name}"].append(iso)


def get_carbon_length(substrate):
    """
    Obtain carbon length from the substrate

    :param substrate: substrate name  
    """
    carbon_length = session.object_space["process_object"].netan["Clen"]
    if substrate in carbon_length:
        return carbon_length[substrate]
    

st.set_page_config(page_title="IsoDesign 2.0", layout="wide")
st.title("Substrates selection")


# Retrieving substrates names from sessI
substrates = session.object_space["process_object"].netan["input"]
# Create columns based on number of inputs
ncols = st.columns(len(substrates), gap="medium")
for index, substrate_name in enumerate(substrates):
    # Column creation depending on the number of substrates
    with ncols[index]:
        # Column title with input name
        st.header(substrate_name)
        # Create a text input for labelling with a default value based on the carbon length
        labelling = st.text_input("Number of tracer atoms", 
                                        key=f"text_{substrate_name}", 
                                        value="0" * get_carbon_length(substrate_name))
        # Columns for lower bound, upper bound, and number of intervals
        lb, ub, step = st.columns(3, gap="medium")
        with lb:
            lower_b=st.text_input("Lower bound", key=f"lb_{substrate_name}", value=100)
        with ub:
            upper_b=st.text_input("Upper bound", key=f"ub_{substrate_name}", value=100)
        with step:
            nb_intervals = st.text_input("Nb intervals", key=f"step_{substrate_name}", value=100)

        # Create an add button to call the add_substrates function with the given parameters
        add_button = st.button("Add",
                                key=f"add_button_{substrate_name}", 
                                on_click=add_substrates, 
                                args=(substrate_name, labelling, nb_intervals, lower_b, upper_b))
        
st.write(" ")        
substrates_selection = st.form("form_substrate")
with substrates_selection:
    st.header("Labels")
    # Create a copy of the dictionary without the "process_object" key
    # Session.object_space contains all objects registered in previous pages
    # Here, the "process_object" object created in the previous page must not be used for the methods to follow 
    objects_without_process = {key: value for key, value in session.object_space.objects.items() if key != "process_object"}

    # display of initiated labels 
    for substrates_name, labelinputs in objects_without_process.items():
        st.header(substrates_name)
        for labelinput in labelinputs:
            st.write(labelinput)
    
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        # generating combinations 
        session.object_space["process_object"].generate_combinations(objects_without_process)
        # linp file generations 
        session.object_space["process_object"].generate_linp_files()
        session.object_space["process_object"].generate_vmtf_file()
        # session.object_space["process_object"].files_copy()
        
        st.switch_page(r"pages/3_Influx_simulation.py")