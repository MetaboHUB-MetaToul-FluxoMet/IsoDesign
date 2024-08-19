import tkinter as tk
from tkinter import filedialog
import pandas as pd


from isodesign.base.process import Process

import isodesign
import logging 
import pickle

import streamlit as st
from sess_i.base.main import SessI
from pathlib import Path


logger = logging.getLogger("IsoDesign")
logger.setLevel(logging.DEBUG)

session = SessI(
    session_state=st.session_state,
    page="Upload_data"
)



def logger_setup(output_path, debug_mode=False):
    """ 
    Set up a logger for the application. This method creates a logging handler
    that writes logs to a file and a stream handler to the console. 
    The log level is set to INFO by default. If debug_mode is set to True, 
    the log level is set to DEBUG.

    :param output_path: the path where the log file will be saved
    :param debug_mode: if True, the logger will be set to debug mode.
    :return: the configured logger 

    """
    try:
        handler = logging.FileHandler(f"{output_path}/log.txt", mode="w")
    except FileNotFoundError:  
        raise FileNotFoundError("The output path does not exist.")
    
    stream = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    stream.setLevel(logging.INFO)

    if debug_mode:
        handler.setLevel(logging.DEBUG)
        stream.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-Method %(funcName)s-%(message)s")
    handler.setFormatter(formatter)
    stream.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.addHandler(stream)
    return logger


# def save_pickle(session, path):
#     with open(str(f"{path}/session.pkl"), "wb") as file_handler:
#         pickle.dump(session, file_handler)


st.set_page_config(page_title=f"IsoDesign (v {isodesign.__version__})")
st.title(f"Welcome to IsoDesign (v {isodesign.__version__})")

# Check if a new version is available
try:
    isodesign_path = Path(isodesign.__file__).parent
    with open(str(Path(isodesign_path, "last_version.txt")), "r") as f:
        lastversion = f.read()
    if lastversion != isodesign.__version__:
        # change the next line to streamlit
        update_info = st.info(
            f'New version available ({lastversion}). '
            f'You can update isodesign with: "pip install --upgrade '
            f'isodesign". Check the documentation for more '
            f'information.'
        )
except Exception:
    pass

# checkbox to activate the debug mode  
debug_mode = st.sidebar.checkbox('Verbose logs',
                                  help = "Useful in case of trouble. Join it to the issue on github.")

with st.container(border=True):
    # Set up tkinter
    root = tk.Tk()
    root.withdraw()

    # Make folder picker dialog appear on top of other windows
    root.wm_attributes('-topmost', 1)
    # Folder picker button
    st.subheader('Load your file folder',
                help = "It must contain at least one \
            .netw file (i.e. metabolic network model),\
            one .miso file (i.e. isotopic measurements) and \
            one .mflux file (i.e. input and output fluxes). ")

    input_button = st.button(
            label="Browse folder",
            key="input_button")


    if input_button:
        # Show folder picker dialog in GUI
        input_folder_path = filedialog.askdirectory(master=root)

        session.register_widgets({"input_folder_path": input_folder_path})
        
        process_object = Process()
        process_object.get_path_input_folder(input_folder_path)
        # Store all model names in folder in a list
        process_object.get_model_names()
        # Register the process object to the session
        session.register_object(process_object, "process_object")
        
        
    st.text_input("**Folder path** :\n", "No folder selected" if not session.widget_space["input_folder_path"]
                    else session.widget_space["input_folder_path"], key="input_folder_path")

    st.subheader("Load results folder path")
    output_button= st.button(
            label="Browse folder",
            key="output_button")
        
    if output_button:
        output_folder_path = filedialog.askdirectory(master=root)
        session.register_widgets({"output_folder_path": output_folder_path})

        # Create a folder to store the results
        session.object_space["process_object"].results_folder_creation(output_folder_path)
        
        # Set up the logger
        logger_setup(session.object_space["process_object"].res_folder_path, debug_mode)
        
    st.text_input("**Folder path** :", "No folder selected" if not session.widget_space["output_folder_path"]
                    else session.widget_space["output_folder_path"], key="output_folder_path")

# If the folder paths are registered, the user can choose the model to use
if session.widget_space["input_folder_path"] and session.widget_space["output_folder_path"]:
    with st.container(border=True):
        # Selectbox to choose from all model names retrieved from the folder   
        model_names = session.object_space["process_object"].model_names

        # If the model name has already been chosen, it is displayed in the selectbox 
        # otherwise the first model name is displayed
        netw_choice = st.selectbox("Choose your netw file", 
                            options=model_names,
                            key="netw_choice",
                            index=model_names.index(session.widget_space["netw_choice"]) if session.widget_space["netw_choice"] is not None else 0)
        
        session.register_widgets({"netw_choice": netw_choice})
        submit = st.button("Submit",
                           key="submit_button")
        
    if submit :
        session.object_space["process_object"].model_name=netw_choice 
        # Register the state (TRUE) of the submit button 
        session.register_widgets({"submit_button": submit})               


if session.widget_space["submit_button"]:
    # Import and analysis of model files 
    session.object_space["process_object"].load_model(session.object_space["process_object"].model_name)
    session.object_space["process_object"].model_analysis()

    with st.container(border=True):
        st.subheader("Network analysis")
        # Tabs for network model analysis
        list_tab = ["Label input", "Isotopic measurements", "Inputs/Outputs", "Fluxes", "Network"]
        # If the mmet file is present in the model files, the concentrations tab is added
        if "mmet" in session.object_space["process_object"].mtf_files.keys():
            list_tab.append("Concentrations")

        tabs = st.tabs(list_tab)

        with tabs[0]:
            # Display labels input
            with st.container(height=400):
                for inputs in session.object_space["process_object"].netan["input"]:
                    st.write(inputs)

        with tabs[1]:
            # Display miso file content
            st.dataframe(session.object_space["process_object"].mtf_files["miso"].data, hide_index=True, height=400,width=600)

        with tabs[2]:
            # Display inputs, intermediate and outputs metabolites
            with st.container(height=400):
                inputs, intermediate, outputs = st.columns(3, gap = 'small')
                with inputs:
                    st.subheader("Inputs")
                    for inputs_netw in session.object_space["process_object"].netan["input"]:
                        st.write(inputs_netw)
                with intermediate:
                    st.subheader("Intermediates")
                    for intermediate in session.object_space["process_object"].netan["metabs"]:
                        st.write(intermediate)
                with outputs:
                    st.subheader("Outputs")
                    for outputs in session.object_space["process_object"].netan["output"]:
                        st.write(outputs)  

        with tabs[3]:
            # Display tvar file content 
            st.dataframe(session.object_space["process_object"].mtf_files["tvar"].data, hide_index=True, height=400, width=600)

        with tabs[4]:
            # Display a dataframe with reactions and their names and metabolic pathways  
            netw_dataframe = pd.DataFrame({
                        "Name" : session.object_space["process_object"].mtf_files['netw'].data[0],
                        "Reaction" : session.object_space["process_object"].mtf_files['netw'].data[1],
                        })

            pathways = []
            
            for reaction_name in netw_dataframe['Name']:
                # Remove ':' from the name (name-reaction separator in netw file)
                # Give exactly the same reaction names as those contained in the netan dictionary
                reaction_name = reaction_name.replace(":","")
                # Append a list of pathways associated with the name to the 'pathways' list
                pathways.append([pathway for pathway, reaction in session.object_space["process_object"].netan["pathway"].items() if reaction_name in reaction])
            
            netw_dataframe["Pathway"] = pathways

            st.dataframe(netw_dataframe, hide_index=True, height=400, width=600)

        if "Concentrations" in list_tab:
            with tabs[5]:
                # Display mmet file content
                st.dataframe(session.object_space["process_object"].mtf_files["mmet"].data, hide_index=True, height=400, width=600)

    next = st.button("Next page")
    if next:
        # Go to next page
            st.switch_page(r"pages/2_Generate_labels_input.py")


