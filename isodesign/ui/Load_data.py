import tkinter as tk
from tkinter import filedialog
import pandas as pd
import isodesign
from isodesign.base.process import Process
from isodesign.base.io import IoHandler

import logging 
import pickle

import streamlit as st
from sess_i.base.main import SessI
from pathlib import Path


logger = logging.getLogger("IsoDesign")
logger.setLevel(logging.DEBUG)

session = SessI(
    session_state=st.session_state,
    page="Load_data")

#############
# FUNCTIONS #
#############
        
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

    formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
    handler.setFormatter(formatter)
    stream.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.addHandler(stream)
    return logger

# def overwrite_results_dir_path():
#     """
#     Overwrite the output folder path.
#     """
#     session.register_widgets({"overwrite_button": False})
#     process_object.clear_tmp_folder(session.widget_space["results_dir_path"])
#     session.register_widgets({"submit_button": True})

########
# MAIN #
########

st.set_page_config(page_title=f"IsoDesign (v{isodesign.__version__})")
st.title(f"Welcome to IsoDesign (v{isodesign.__version__})")

st.space("small")

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

####### SIDEBAR ########
st.sidebar.markdown("## Load a previous session")

# Load a pickle file if it exists
upload_pickle = st.sidebar.file_uploader("Load a previous session file.",
                                         key="upload_pickle",
                                         help = 'File with pickle extension (".pkl").',
                                         type= ["pkl"],
                                         label_visibility="collapsed")

if upload_pickle:
    with upload_pickle as session_file:
        pickle_file = pickle.load(session_file)
    # Retrieves the instances stored in the pickle    
    session.object_space["process_object"] = pickle_file.get("process_object")
    session.object_space["io_object"] = pickle_file.get("io_object")
    
    # Retrieves the state of the widgets and/or their values
    session.register_widgets({"input_file_path" : session.object_space["io_object"].netw_file_path,
                              "output_path" : session.object_space["io_object"].results_dir_path,
                              "submit_button": True,
                              "upload_pickle": upload_pickle})

st.sidebar.markdown("## Debug mode")
# checkbox to activate the debug mode  
debug_mode = st.sidebar.checkbox('Verbose logs',
                                  help = "Useful in case of trouble. Join it to the issue on github.",
                                  key="debug_mode")

st.sidebar.divider()
st.sidebar.link_button("Documentation",
                        url="https://isodesign.readthedocs.io/en/latest/",
                        help = "Documentation of IsoDesign.",
                        key="doc_button"
                       )
with st.sidebar : 
    with st.expander("Legal information"):
        st.markdown(f"""
        **Authors :** Rochelle KOUAKOU, Loic LE GREGAM, Pierre MILLARD, Serguei SOKOL, [INRAE](https://www.inrae.fr/)/ 
                    [TBI](https://www.toulouse-biotechnology-institute.fr/)/[MetaboHUB](https://www.metabohub.fr/)  
        **Version :** `{isodesign.__version__}`  
        **License :** [GPLv3](https://www.gnu.org/licenses/)  
        **Copyright 2025, [INSA](https://www.insa-toulouse.fr/)/[INRAE](https://www.inrae.fr/)/[CNRS](https://www.cnrs.fr/fr)**
        """)
####### SIDEBAR END ########

# Initialises the IoHandler instance if it is not present in SessI
if not session.object_space["io_object"]:
    session.object_space["io_object"] = IoHandler()

io = session.object_space["io_object"]

with st.container(border=True):
    st.subheader('Load your network file',
                help = 'File with ".netw" extension (containing all reactions and transition labels)')

    if "input_file_path" not in session.widget_space.widgets:
        session.widget_space.widgets["input_file_path"] = None

    if "output_path" not in session.widget_space.widgets:
        session.widget_space.widgets["output_path"] = None

    col1, col2 =st.columns([0.3,1.75])
    with col1:
        input_button = st.button(
            label="Browse file",
            key="input_button")

        if input_button:
            # Set up tkinter 
            root = tk.Tk()
            root.withdraw()

            # Make folder picker dialog appear on top of other windows
            root.wm_attributes('-topmost', 1)

            file_path = filedialog.askopenfilename(master = root,
                                                title = "Select a network file",
                                                filetypes=[("netw files", "*.netw")])
            root.destroy()
            
            if file_path:
                session.widget_space.widgets["input_file_path"] = io.get_netw_file_path(file_path)
                session.widget_space.widgets["output_path"] = session.widget_space.widgets["input_file_path"].parent
    with col2:    
        netw_path = st.text_input(
            label="**Netw directory path** :\n",
            value=session.widget_space["input_file_path"],
            placeholder="No folder selected",
            label_visibility="collapsed")
        
        if netw_path:
            session.widget_space.widgets["input_file_path"] = Path(netw_path) 

    st.subheader("Output directory path")
    output_path_folder = st.text_input("**Folder path** :",
                        value=session.widget_space.widgets["output_path"],
                        placeholder="No folder selected",
                        label_visibility="collapsed")
    if output_path_folder:
        session.widget_space.widgets["output_path"] = Path(output_path_folder)

    submit_button = st.button("Submit",
                       key="submit_button")
    
if submit_button:
    # Retrieving and defining the various paths and necessary information in IoHandler instance
    io.netw_file_path = session.widget_space["input_file_path"]
    io.results_dir_path = session.widget_space["output_path"]
    io.model_dir_path = io.netw_file_path.parent
    io.model_name = io.netw_file_path.stem

if io.model_name:
    data = io.load_metabolic_netw_model(io.model_name, io.model_dir_path)

    # Initialises the Process instance if it is not present in SessI 
    if not session.object_space["process_object"]:
        session.object_space["process_object"] = Process(data)
    process_object = session.object_space["process_object"]

    io.generate_tmp_folder(data)
    logger_setup(io.tmp_folder_path, debug_mode)
    logger.info(f"IsoDesign version: {isodesign.__version__}")
    logger.info(f"Network file path: {io.netw_file_path}")
    logger.info(f"Results directory path: {io.results_dir_path}")

    try:
        if not process_object.netan:
            with st.spinner("Uploading files..."):
                process_object.model_analysis(io.model_dir_path, io.model_name)
    except Exception as e:
        st.error(f"An error occured : {e}")
        st.stop()

    if process_object.netan:        
        with st.container(border=True):
            st.subheader("Network analysis")
            # Tabs for network model analysis
            list_tab = ["Label inputs", "Isotopic measurements", "In/Out", "Fluxes", "Network"]
            # If the mmet file is present in the model files, the concentrations tab is added
            if "mmet" in process_object.data.keys():
                list_tab.append("Concentrations")
            tabs = st.tabs(list_tab)

            with tabs[0]:
                # Display labels input
                with st.container(height=400):
                    for inputs in process_object.netan["input"]:
                        st.write(inputs)

            with tabs[1]:
                # Display miso file content
                st.dataframe(process_object.data["miso"].data, 
                            hide_index=True, 
                            height=400,
                            width=600,
                            key="dataframe_miso")

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
                st.dataframe(process_object.data["tvar"].data, 
                            hide_index=True, 
                            height=400, 
                            width=600,
                            key="dataframe_tvar")

            with tabs[4]:
                # Display a dataframe with reactions and their names and metabolic pathways  
                netw_dataframe = pd.DataFrame({
                            "Name" : process_object.data['netw'].data[0],
                            "Reaction" : process_object.data['netw'].data[1],
                            })

                pathways = []
                
                for reaction_name in netw_dataframe['Name']:
                    # Remove ':' from the name (name-reaction separator in netw file)
                    # Give exactly the same reaction names as those contained in the netan dictionary
                    reaction_name = reaction_name.replace(":","")
                    # Append a list of pathways associated with the name to the 'pathways' list
                    pathways.append([pathway for pathway, reaction in process_object.netan["pathway"].items() if reaction_name in reaction])
                
                netw_dataframe["Pathway"] = pathways

                st.dataframe(netw_dataframe, hide_index=True, height="auto", width="stretch", key="dataframe_netw")
        
        next_button = st.button("Next page",
                                key="next_button")

        if next_button:
            # Instances to serialize
            to_pickle = {
                "process_object":process_object,
                "io_object":io
            }

            process_object.save_process_to_file(to_pickle, io.results_dir_path, io.model_name)
            # Go to next page
            st.switch_page(r"pages/2_Define_label_inputs.py")



    
