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

logging_mode = st.checkbox('Logging mode')

# Set up tkinter
root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

st.write(" ")
# Folder picker button
st.write('Please select a folder:')

clicked = st.button(
        label="Folder Picker",
        key="clicked_home")
 
if clicked:
    # Show folder picker dialog in GUI
    folder_path = filedialog.askdirectory(master=root)
    session.register_widgets({"folder_path": folder_path})
    
    process_object = Process()
    session.register_object(process_object, "process_object")
  
    process_object.initialize_data(folder_path)

st.write("**Selected folder** :\n", session.widget_space["folder_path"])

input_folder = session.object_space["process_object"]

if session.widget_space["folder_path"]:
    netw_selection = st.form("form_netw")
    with netw_selection:
        netw_choice = st.selectbox("Choose your netw file", 
                          options=input_folder.netw_files_prefixes,
                          key="netw_choice",
                          index=None)
        
        session.register_widgets({"netw_choice": netw_choice})
        session.register_widgets({"form_netw": netw_selection})

        submitted = st.form_submit_button("Submit")
        input_folder.prefix=netw_choice                

if session.widget_space["netw_choice"]:
    # File upload and network analysis based on registered prefix
    input_folder.load_file(input_folder.prefix)
    input_folder.input_network_analysis()
    form = st.form("form_home")
    with form:
        # Tabs for network analysis
        ntw_input, miso, reactants, fluxes, reactions = st.tabs(["Label input", "Miso", "Reactants", "Fluxes", "Reactions"])
        with ntw_input:
            with st.container(height=400):
                for inputs in input_folder.netan["input"]:
                            st.write(inputs)
            with miso:
                st.dataframe(input_folder.imported_files_dict["miso"].data, hide_index=True, height=400,width=600)

            with reactants:
                with st.container(height=300):
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
                    st.dataframe(input_folder.imported_files_dict["tvar"].data, hide_index=True, height=300, width=600)

                with reactions:
                    data = pd.DataFrame({
                        "Name" : input_folder.imported_files_dict['netw'].data[0][:-1],
                        "Reaction" : input_folder.imported_files_dict['netw'].data[1]
                    })
                    st.dataframe(data, hide_index=True, height=300, width=500)
        submitted = st.form_submit_button("Submit")
    session.register_widgets({"form_home": form})
        
    