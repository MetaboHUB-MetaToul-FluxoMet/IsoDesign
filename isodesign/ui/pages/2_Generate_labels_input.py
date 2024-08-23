import streamlit as st
from sess_i.base.main import SessI


session = SessI(
        session_state=st.session_state,
        page="2_Generate_labels_input.py")

# Retrieving substrates names from sessI
process_object = session.object_space["process_object"]


def remove_substrates(substrate, labelling):
    """
    Remove substrates from the isotopomer dictionary.
    In the dictionary, all substrates have the same name. They can 
    therefore be differentiated by labelling. This parameter is used 
    to remove the correct substrate. 
    
    :param substrate: substrate name
    :param labelling: labelling for isotopomer
    
    """
    
    for substrate in process_object.isotopomer_dict[f"{substrate_name}"]:
        if substrate.labelling == labelling:
            process_object.isotopomer_dict[f"{substrate_name}"].remove(substrate)
       

def get_carbon_length(substrate):
    """
    Obtain the carbon number of the substrate. 
    This number is retrieved from the netan dictionary (Process class). 

    :param substrate: substrate name  
    """
    carbon_length = process_object.netan["Clen"]
    if substrate in carbon_length:
        return carbon_length[substrate]



def add_form(count=0):
    """
    Create a form to add substrates.

    """
    
    with st.form(f"form_{substrate_name}_{count}"):
        labelling, price = st.columns(2)
        with labelling:
            labelling = st.text_input(f"Number of tracer atoms : {get_carbon_length(substrate_name)}", 
                                  key=f"labelling_{substrate_name}_{count}", 
                                  value="0" * get_carbon_length(substrate_name))
        
        with price:
            price = st.text_input("Price", 
                                  key=f"price_{substrate_name}_{count}", 
                                  value=0,
                                  help="Price of the substrate")

        lb, ub, step = st.columns(3, gap="medium")
        with lb:
            lower_b = st.text_input("Lower bound", key=f"lb_{substrate_name}_{count}", value=100)
        with ub:
            upper_b = st.text_input("Upper bound", key=f"ub_{substrate_name}_{count}", value=100)
        with step:
            nb_intervals = st.text_input("Nb intervals", key=f"step_{substrate_name}_{count}", value=100)
        # 
        add_col, remove_col = st.columns([1, 10])
        with add_col:
            add = st.form_submit_button("Add")
            if add:
                session.register_widgets({f"add_{count}_{substrate_name}" : add})
                process_object.generate_isotopomer(substrate_name, labelling, int(nb_intervals), int(lower_b), int(upper_b), float(price))
        if count > 0:
            with remove_col:
                remove = st.form_submit_button("Remove")
                if remove:
                    remove_substrates(substrate_name, labelling)
                    session.widget_space.widgets.pop(f"add_{count}_{substrate_name}")               
    # If the add button is clicked, the function is called again to generate a new form
    if session.widget_space[f"add_{count}_{substrate_name}"]:
        count += 1
        add_form(count)
        

st.set_page_config(page_title="IsoDesign")
st.title("Generate labels input")

# Add a space between page title and content 
st.write(" ")
# Create tabs according to the number of labeled substrates 
# Labeled substrates are retrieved from the netan dictionary (argument in Process class) 
tabs=st.tabs(list(process_object.netan["input"]))
for index, substrate_name in enumerate(process_object.netan["input"]):
    with tabs[index]:
        st.header(substrate_name)
        # Add a form to add labeled substrates
        add_form()

submit = st.button("Submit")
if submit:
    session.object_space["process_object"].generate_combinations()
    # linp file generations 
    session.object_space["process_object"].generate_linp_files()
    session.object_space["process_object"].generate_vmtf_file()
    session.object_space["process_object"].copy_files()
    st.switch_page(r"pages\3_Simulation_options.py")

st.write(session.object_space["process_object"].isotopomers)
st.write(session)

    
