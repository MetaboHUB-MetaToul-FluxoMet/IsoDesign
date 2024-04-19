import tkinter as tk
from tkinter import filedialog
import pandas as pd

from isodesign.base.calculation import Process

import streamlit as st
from sess_i.base.main import SessI


st.set_page_config(page_title="IsoDesign 2.0")
st.title("Welcome to IsoDesign 2.0")

session = SessI(
    session_state=st.session_state,
    page="upload"
)

logging_mode = st.checkbox('Debug mode')

# Set up tkinter
root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

st.write(" ")
# Folder picker button
st.subheader('Select input folder')

clicked = st.button(
        label="Browse folders",
        key="input_button")
 
if clicked:
    # Show folder picker dialog in GUI
    folder_path = filedialog.askdirectory(master=root)
    session.register_widgets({"folder_path": folder_path})
    
    # Process class manages most of the steps initiated within the tool
    process_object = Process()
    session.register_object(process_object, "process_object")
  
    process_object.initialize_data(folder_path)

st.write("**Selected folder** :\n", session.widget_space["folder_path"])

# Get process_object from object_space to retrieve attributes 
input_folder = session.object_space["process_object"]

if session.widget_space["folder_path"]:
    netw_selection = st.form("form_netw_choice")
    with netw_selection:
        # Selectbox to choose from all prefixes retrieved from the folder
        netw_choice = st.selectbox("Choose your netw file", 
                          options=input_folder.netw_files_prefixes,
                          key="netw_choice",
                          index=None)
        
        session.register_widgets({"netw_choice": netw_choice})

        submitted = st.form_submit_button("Submit")
        # The chosen prefix is stored and will be used again
        input_folder.prefix=netw_choice                

if session.widget_space["netw_choice"]:
    # File upload and network analysis based on registered prefix
    input_folder.load_file(input_folder.prefix)
    input_folder.input_network_analysis()

    netan_container = st.container(border=True)
    with netan_container:
        
        st.subheader("Network analysis")
        # Tabs for network analysis
        label_input, miso, reactants, fluxes, reactions = st.tabs(["Label input", "Isotopic measurements", "Reactants", "Fluxes", "Reactions"])
        with label_input:
            with st.container(height=400):
                for inputs in input_folder.netan["input"]:
                    st.write(inputs)

            with miso:
                # Display miso file content
                st.dataframe(input_folder.imported_files_dict["miso"].data, hide_index=True, height=400,width=600)

            with reactants:
                with st.container(height=400):
                    subs, prods = st.columns(2)
                    with subs:
                        st.header("Substrates")
                        for substrate in input_folder.netan["subs"]:
                            st.write(substrate)
                    with prods:
                        st.header("Products")
                        for product in input_folder.netan["prods"]:
                            st.write(product)  

                with fluxes:
                    # Display tvar file content 
                    st.dataframe(input_folder.imported_files_dict["tvar"].data, hide_index=True, height=400, width=600)

                with reactions:
                    # Display netw file content
                    data = pd.DataFrame({
                        "Name" : input_folder.imported_files_dict['netw'].data[0],
                        "Reaction" : input_folder.imported_files_dict['netw'].data[1]
                    })
                    st.dataframe(data, hide_index=True, height=400, width=600)

        st.subheader("Select output folder")

        output_button= st.button(
            label="Browse folders",
            key="output_button")
        
        if output_button:
            output_path = filedialog.askdirectory(master=root)
            session.register_widgets({"output_path": output_path})

            # stores the output destination 
            # will be reused as the output path for generating files from Isodesign 
            input_folder.path_isodesign_folder = output_path
            
            st.write("**Selected folder** :\n", output_path)

    next = st.button("Next page")
    if next:
        # Go to next page
        st.switch_page(r"pages/2_Substrates_selection.py")



    
    
        
    