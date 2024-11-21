import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

from isodesign.base.process import Process

import isodesign
import logging 
import pickle

import streamlit as st
from sess_i.base.main import SessI
from pathlib import Path


logger = logging.getLogger("IsoDesign")
logger.setLevel(logging.DEBUG)

#############
# FUNCTIONS #
#############

def get_path_netw():
    """ 
    Open a file dialog to select a network file.
    """
    session.register_widgets({"input_button": True})
    # Set up tkinter
    root = tk.Tk()
    root.withdraw()

    # Make folder picker dialog appear on top of other windows
    root.wm_attributes('-topmost', 1)

    netw_directory_path = filedialog.askopenfilename(master = root,
                                                       title = "Select a network file",
                                                       filetypes=[("netw files", "*.netw")])
    session.register_widgets({"netw_directory_path": netw_directory_path})
    

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

def change_output_folder_path():
    """
    Change the output folder path.
    """
    session.register_widgets({"output_folder_path": output_path_folder})

# def overwrite_output_folder_path():
#     """
#     Overwrite the output folder path.
#     """
#     session.register_widgets({"overwrite_button": False})
#     process_object.clear_tmp_folder(session.widget_space["output_folder_path"])
#     session.register_widgets({"submit_button": True})

########
# MAIN #
########

session = SessI(
    session_state=st.session_state,
    page="Upload_data"
)

st.set_page_config(page_title=f"IsoDesign (v{isodesign.__version__})")
st.title(f"Welcome to IsoDesign (v{isodesign.__version__})")

# Check if a new version is available
try:
    isodesign_path = Path(isodesign.__file__).parent
    with open(str(Path(isodesign_path, "last_version.txt")), "r") as f:
        lastversion = f.read()
    if lastversion != isodesign.__version__:
        # change the next line to streamlit
        update_info = st.info(
            f'New version available ({lastversion}). '
            f'You can update IsoDesign with: "pip install --upgrade '
            f'isodesign". Check the documentation for more '
            f'information.'
        )
except Exception:
    pass

st.sidebar.markdown("## Load a session")
# Load a pickle file if it exists
upload_pickle = st.sidebar.file_uploader("Load a previous session file.",
                                         key="upload_pickle",
                                         help = 'File with pickle extension (".pkl").')
if upload_pickle:
    with upload_pickle as session_file:
        process_object = pickle.load(session_file)
    
    session.object_space["process_object"] = process_object
    # Retrieves the state of the submit button 
    session.register_widgets({"submit_button": True})


if not session.object_space["process_object"]:
    session.object_space["process_object"] = Process()

process_object = session.object_space["process_object"]

st.sidebar.divider()
st.sidebar.markdown("## Debug mode")
# checkbox to activate the debug mode  
debug_mode = st.sidebar.checkbox('Verbose logs',
                                  help = "Useful in case of trouble. Join it to the issue on github.")


with st.container(border=True):

    st.subheader('Load your network file',
                help = 'File with ".netw" extension (containing all reactions and transition labels)')

    input_button = st.button(
            label="Browse file",
            key="input_button",
            on_click=get_path_netw)
    
    if session.widget_space["netw_directory_path"]:
        process_object.get_path_input_netw(session.widget_space["netw_directory_path"])
    
    st.text_input("**Netw directory path** :\n", 
                    "No folder selected" if not process_object.netw_directory_path
                    else process_object.netw_directory_path, 
                    key="input_file_path")
    

    st.subheader("Output directory path")
    output_path_folder = st.text_input("**Folder path** :", 
                        value="No folder selected" if not process_object.model_directory_path
                        else process_object.model_directory_path, 
                        key="output_folder_path",
                        on_change=change_output_folder_path)
    
    session.register_widgets({"output_folder_path": output_path_folder})
    
    
    if os.path.exists(Path(f"{session.widget_space['output_folder_path']}/{process_object.model_name}_tmp")):
        st.warning(f"The folder '{process_object.model_name}_tmp' already exists. \
                   If you continue, it will be overwritten. If you don't want to overwrite it,\
                   please change the output folder path and click on the 'Submit' button.")
       
    
    submit_button = st.button("Submit",
                       key="submit_button")

if submit_button:
    # Check if the folder already exists
        session.register_widgets({"submit_button": submit_button})
    
        
if session.widget_space["submit_button"]:
    
    process_object.create_tmp_folder(session.widget_space["output_folder_path"])
    logger_setup(process_object.tmp_folder_path, debug_mode)
   # Import and analysis of model files 
    try:
        process_object.load_model()
        if not process_object.netan:
            with st.spinner("Uploading files..."):
                process_object.analyse_model()
    except Exception as e:
        st.error(f"An error occured : {e}")
        st.stop()
    
    
if process_object.netan:        
    with st.container(border=True):
        st.subheader("Network analysis")
        # Tabs for network model analysis
        list_tab = ["Label input", "Isotopic measurements", "Inputs/Outputs", "Fluxes", "Network"]
        # If the mmet file is present in the model files, the concentrations tab is added
        if "mmet" in process_object.mtf_files.keys():
            list_tab.append("Concentrations")

        tabs = st.tabs(list_tab)

        with tabs[0]:
            # Display labels input
            with st.container(height=400):
                for inputs in process_object.netan["input"]:
                    st.write(inputs)

        with tabs[1]:
            # Display miso file content
            st.dataframe(process_object.mtf_files["miso"].data, 
                         hide_index=True, 
                         height=400,
                         width=600)

        with tabs[2]:
            # Display inputs, intermediate and outputs metabolites
            with st.container(height=400):
                inputs, intermediate, outputs = st.columns(3, gap = 'small')
                with inputs:
                    st.subheader("Inputs")
                    for inputs_netw in process_object.netan["input"]:
                        st.write(inputs_netw)
                with intermediate:
                    st.subheader("Intermediates")
                    for intermediate in process_object.netan["metabs"]:
                        st.write(intermediate)
                with outputs:
                    st.subheader("Outputs")
                    for outputs in process_object.netan["output"]:
                        st.write(outputs)  

        with tabs[3]:
            # Display tvar file content 
            st.dataframe(process_object.mtf_files["tvar"].data, 
                         hide_index=True, 
                         height=400, 
                         width=600)

        with tabs[4]:
            # Display a dataframe with reactions and their names and metabolic pathways  
            netw_dataframe = pd.DataFrame({
                        "Name" : process_object.mtf_files['netw'].data[0],
                        "Reaction" : process_object.mtf_files['netw'].data[1],
                        })

            pathways = []
            
            for reaction_name in netw_dataframe['Name']:
                # Remove ':' from the name (name-reaction separator in netw file)
                # Give exactly the same reaction names as those contained in the netan dictionary
                reaction_name = reaction_name.replace(":","")
                # Append a list of pathways associated with the name to the 'pathways' list
                pathways.append([pathway for pathway, reaction in process_object.netan["pathway"].items() if reaction_name in reaction])
            
            netw_dataframe["Pathway"] = pathways

            st.dataframe(netw_dataframe, hide_index=True, height=400, width=600)

        if "Concentrations" in list_tab:
            with tabs[5]:
                # Display mmet file content
                st.dataframe(process_object.mtf_files["mmet"].data, hide_index=True, height=400, width=600)

    next_button = st.button("Next page",
                            key="next_button")
    if next_button:
        session.register_widgets({"next_button": next_button})
        process_object.save_process_to_file()
        # Go to next page
        st.switch_page(r"pages/2_Labels_input.py")





    
