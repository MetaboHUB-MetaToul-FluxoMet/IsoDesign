import tkinter as tk
from tkinter import filedialog
import pandas as pd

from isodesign.base.process import Process

import logging 
import pickle

import streamlit as st
from sess_i.base.main import SessI

# try:
#     with open("session.pkl", "rb") as f:
#         session = pickle.load(f)
# except FileNotFoundError:
#     session = SessI(session_state=st.session_state, page="Home")

st.set_page_config(page_title="IsoDesign")
st.title("Welcome to IsoDesign")

session = SessI(
    session_state=st.session_state,
    page="Upload_data"
)

process_object = Process() if not hasattr(session.object_space, "process_object") else session.get_object("process_object")


logging_mode = st.checkbox('Debug mode')
if logging_mode:
    process_object.logger.setLevel(logging.DEBUG)


st.write(" ")

# st.header("Input/Output folder")
with st.container(border=True):
    
    # Set up tkinter
    root = tk.Tk()
    root.withdraw()

    # Make folder picker dialog appear on top of other windows
    root.wm_attributes('-topmost', 1)
    # Folder picker button
    st.subheader('Load a folder')

    input_button = st.button(
            label="Browse folder",
            key="input_button")

    if input_button:
        # Show folder picker dialog in GUI
        input_folder_path = filedialog.askdirectory(master=root)
        session.register_widgets({"input_folder_path": input_folder_path})
        
        # Store the path to the input folder and get all prefixes via network files 
        process_object.get_path_input_folder(input_folder_path)
        # Register the process object to the session
        session.register_object(process_object, "process_object")

    st.write("**Selected folder path** :\n", session.widget_space["input_folder_path"])

    st.subheader("Results output folder")
    output_button= st.button(
            label="Browse folder",
            key="output_button")
        
    if output_button:
        output_folder_path = filedialog.askdirectory(master=root)
        session.register_widgets({"output_folder_path": output_folder_path})
        # stores the output destination 
        # will be reused as the output path for generating files from Isodesign 
        session.object_space["process_object"].res_folder_path = output_folder_path 

    st.write("**Results output folder path** :\n", session.widget_space["output_folder_path"])
    

# process_object = session.get_object("process_object")

if session.widget_space["output_folder_path"]:

    with st.container(border=True):
        # Selectbox to choose from all prefixes retrieved from the folder   
        prefix_list = session.object_space["process_object"].netw_files_prefixes
        netw_choice = st.selectbox("Choose your netw file", 
                            options=prefix_list,
                            key="netw_choice",
                            index=prefix_list.index(session.widget_space["netw_choice"]) if session.widget_space["netw_choice"] is not None else 0)
        
        session.register_widgets({"netw_choice": netw_choice})
        submit = st.button("Submit",
                           key="submit_button")
        
        if submit :
            # The chosen prefix is stored and will be used again
            session.object_space["process_object"].prefix=netw_choice 
            session.register_widgets({"submit_button": submit})               


if session.widget_space["submit_button"]:
    # File upload and network analysis based on registered prefix
    session.object_space["process_object"].load_mtf_files(session.object_space["process_object"].prefix)
    session.object_space["process_object"].input_network_analysis()

    with st.container(border=True):
        st.subheader("Network analysis")
        # Tabs for network analysis
        list_tab = ["Label input", "Isotopic measurements", "Inputs/Outputs", "Fluxes", "Network"]
        
        if "mmet" in session.object_space["process_object"].imported_files_dict.keys():
            list_tab.append("Concentrations")

        tabs = st.tabs(list_tab)

        with tabs[0]:
            # Display labels input
            with st.container(height=400):
                for inputs in session.object_space["process_object"].netan["input"]:
                    st.write(inputs)

        with tabs[1]:
            # Display miso file content
            st.dataframe(session.object_space["process_object"].imported_files_dict["miso"].data, hide_index=True, height=400,width=600)

        with tabs[2]:
            with st.container(height=400):
                inputs, outputs = st.columns(2)
                with inputs:
                    st.header("Inputs")
                    for inputs_netw in session.object_space["process_object"].netan["input"]:
                        st.write(inputs_netw)
                with outputs:
                    st.header("Outputs")
                    for outputs in session.object_space["process_object"].netan["output"]:
                        st.write(outputs)  

        with tabs[3]:
            # Display tvar file content 
            st.dataframe(session.object_space["process_object"].imported_files_dict["tvar"].data, hide_index=True, height=400, width=600)

        with tabs[4]:
            # Display a dataframe with reactions and their names and metabolic pathways  
            data = pd.DataFrame({
                        "Name" : session.object_space["process_object"].imported_files_dict['netw'].data[0],
                        "Reaction" : session.object_space["process_object"].imported_files_dict['netw'].data[1],
                        })

            pathways = []

            for name in data['Name']:
                name = name.replace(":","")
                # Append a list of pathways associated with the name to the 'pathways' list
                pathways.append([pathway for pathway, reaction in session.object_space["process_object"].netan["pathway"].items() if name in reaction])
            
            data["Pathway"] = pathways

            st.dataframe(data, hide_index=True, height=400, width=600)

        if "Concentrations" in list_tab:
            with tabs[5]:
                # Display mmet file content
                st.dataframe(session.object_space["process_object"].imported_files_dict["mmet"].data, hide_index=True, height=400, width=600)

    next = st.button("Next page")

    if next:
        # with open("session.pkl", "wb") as f:
        #     pickle.dump(session, f)
        
        # Go to next page
        st.switch_page(r"pages/2_Generate_labels_input.py")



    
    
        
    