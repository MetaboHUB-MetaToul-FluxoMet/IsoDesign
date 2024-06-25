import streamlit as st
from sess_i.base.main import SessI
from isodesign.base.score import ScoreHandler
import pandas as pd
from matplotlib import pyplot as plt

session = SessI(
        session_state=st.session_state,
        page="4_Analysis2")

st.set_page_config(page_title="IsoDesign 2.0", layout="wide")
st.title("Analysis")

def filter(selected_flux, selected_kind,selected_pathway):
    session.object_space['process_object'].data_filter(fluxes_names = selected_flux, kind = selected_kind, pathways=selected_pathway)
        

dataframe = session.object_space['process_object'].summary_dataframe
filtered_dataframe = session.object_space['process_object'].filtered_dataframe

st.data_editor(filtered_dataframe if filtered_dataframe is not None else dataframe,
               column_config={
                    "Choose":st.column_config.CheckboxColumn(
                    "Choose",
                    default=False
                    )
                },
            hide_index=True,
            disabled=False)


with st.expander("**Apply a filter**"):
    st.write("Filter by : ")
    fluxes_name, kind, pathway = st.columns(3)
    with fluxes_name:
        selected_flux=(st.multiselect(label="Fluxes_name", 
                                      options=filtered_dataframe["Name"].drop_duplicates() if filtered_dataframe is not None else dataframe["Name"].drop_duplicates(), 
                                      label_visibility="collapsed",
                                      placeholder= "Flux"))
        
    with kind:
        selected_kind=(st.multiselect(label="kind", 
                                      options=["NET", "XCH", "METAB"], 
                                      label_visibility="collapsed", 
                                      placeholder="Kind"))
        
    with pathway:
        selected_pathway=(st.multiselect(label="Pathway", 
                                         options=session.object_space['process_object'].netan["pathway"].keys(), 
                                         label_visibility="collapsed", placeholder="Pathway"))
        
        
    submit=st.button("Submit",
                     on_click=filter,
                     args=(selected_flux, selected_kind,selected_pathway))
    
with st.container(border=True):
    methods, result = st.columns([6, 9], gap="large")
    with methods:
        method_options = st.multiselect("Criterion", 
                                            options=["Sum SDs", "nb of fluxes with SD < lim", "nb of labeled input"])
        if "Sum SDs" in method_options:
            input_weight=st.text_input("Weight_sum_sd", key=f"weight", value=1)
        if "nb of fluxes with SD < lim" in method_options:
            weight_flux = st.text_input("Weight_flux", key=f"weight_flux", value=1)
            input_threshold = st.text_input("Threshold", 
                                                key=f"threshold", 
                                                value=1)
        if "nb of labeled input" in method_options:
            input_labeled_input=st.text_input("Weight_labeled_input", key=f"weight_labeled_input", value=1)
    
        # if len(method_options) > 1:
        #     operation = st.selectbox("Operations", options=["Add", "Multiply", "Divide"])
                

    submitted = st.button("Submit", key="submit_container")
    if submitted:
        score_handler = ScoreHandler(filtered_dataframe.iloc[:, 4:] if filtered_dataframe is not None else dataframe.iloc[:, 4:])
        score_handler.apply_scores(method_options, 
                                       weight_sum_sd=int(input_weight) if "Sum SDs" in method_options else 1,
                                        threshold=int(input_threshold) if "nb of fluxes with SD < lim" in method_options else 1,
                                        weight_flux=int(weight_flux) if "nb of fluxes with SD < lim" in method_options else 1,
                                        labeled_species_dict=dict(session.object_space["process_object"].labeled_species) if "nb of labeled input" in method_options else None,
                                        weight_labeled_input=int(input_labeled_input) if "nb of labeled input" in method_options else 1
                                        )
         

        with result:     
            st.write("")
            dataframe, barplot = st.columns([10, 15])
            with dataframe:                          
                st.dataframe(score_handler.get_scores())
                
            with barplot:
                # plt.bar( score_handler.get_scores()[method_options], height=10, color='blue')
                # st.bar_chart(score_handler.get_scores()
                st.pyplot(score_handler.get_scores().plot(kind='bar').figure)
    
           

add_score = st.button("Add score", key=f"add_score")
    
                