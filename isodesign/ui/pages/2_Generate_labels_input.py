import streamlit as st
from sess_i.base.main import SessI
from isodesign.base.isotopomer import Isotopomer


session = SessI(
        session_state=st.session_state,
        page="2_Generate_labels_input2.py")

def add_substrates(substrate_name, labelling, nb_intervals, lower_b, upper_b):
    """
    Create an Isotopomer object from the substrate add

    :param substrate_name: substrate name  
    :param labelling: labelling 
    :param nb_intervals: number of intervals (step)
    :param lower_b: lower bound
    :param upper_b: upper bound
    """

    # Create an Isotopomer object with the given parameters
    iso = Isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b))
    if f"{substrate_name}" not in session.object_space.objects:
        # Register the Isotopomer object in the session object space with a unique key
        session.register_object([iso], key=f"{substrate_name}")
    else:
        session.object_space.objects[f"{substrate_name}"].append(iso)

def remove_substrates(substrate_name, labelling):
    if f"{substrate_name}" in session.object_space.objects:
        for value in session.object_space.objects[f"{substrate_name}"]:
            if value.labelling == labelling:
                session.object_space.objects[f"{substrate_name}"].remove(value)
        # session.object_space.objects[f"s{substrate_name}"].remove(iso)

def get_carbon_length(substrate):
    """
    Obtain carbon length from the substrate

    :param substrate: substrate name  
    """
    carbon_length = session.object_space["process_object"].netan["Clen"]
    if substrate in carbon_length:
        return carbon_length[substrate]



def add_form(count=0):
    """
    Create a form to add substrates

    :param count: counter
    """
    
    with st.form(f"form_{substrate_name}_{count}"):
        labelling = st.text_input(f"Number of tracer atoms : {get_carbon_length(substrate_name)}", 
                                  key=f"text_{substrate_name}_{count}", 
                                  value="0" * get_carbon_length(substrate_name))
        

        lb, ub, step = st.columns(3, gap="medium")
        with lb:
            lower_b = st.text_input("Lower bound", key=f"lb_{substrate_name}_{count}", value=100)
        with ub:
            upper_b = st.text_input("Upper bound", key=f"ub_{substrate_name}_{count}", value=100)
        with step:
            nb_intervals = st.text_input("Nb intervals", key=f"step_{substrate_name}_{count}", value=100)

        add_col, remove_col = st.columns([1, 10])
        with add_col:
            add = st.form_submit_button("Add")
            if add:
                session.register_widgets({f"add_{count}_{substrate_name}" : add})
                add_substrates(substrate_name, labelling, nb_intervals, lower_b, upper_b)
                st.rerun()
        if count > 0:
            with remove_col:
                remove = st.form_submit_button("Remove")
                if remove:
                    remove_substrates(substrate_name, labelling)
                    session.widget_space.widgets.pop(f"add_{count}_{substrate_name}")
                    st.rerun()

    if session.widget_space[f"add_{count}_{substrate_name}"]:
        count += 1
        add_form(count)
        

st.set_page_config(page_title="IsoDesign 2.0")
st.title("Generate labels input")

st.write(" ")
# Retrieving substrates names from sessI
substrates = session.object_space["process_object"].netan["input"]
# Create tabs based on number of inputs
tabs=st.tabs(list(substrates))
for index, substrate_name in enumerate(substrates):
    with tabs[index]:
        st.header(substrate_name)
        add_form()


submit = st.button("Submit")
if submit:
    objects_without_process = {key: value for key, value in session.object_space.objects.items() if key != "process_object"}
    session.object_space["process_object"].generate_combinations(objects_without_process)
    # linp file generations 
    session.object_space["process_object"].generate_linp_files()
    session.object_space["process_object"].generate_vmtf_file()
    session.object_space["process_object"].copy_files()
    st.switch_page(r"pages\3_Simulation_options.py")

# st.write(session)


    
