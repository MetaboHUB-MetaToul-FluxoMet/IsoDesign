import streamlit as st
from sess_i.base.main import SessI
import pandas as pd
import plotly.express as px

session = SessI(
        session_state=st.session_state,
        page="4_Analysis")


def filter(selected_flux, selected_kind,selected_pathway):
    """
    Filter the dataframe based on the selected fluxes, kind and pathways.

    :param selected_flux: the selected fluxes
    :param selected_kind: the selected kind
    :param selected_pathway: the selected pathway
    """
    process_object.data_filter(fluxes_names = selected_flux, kind = selected_kind, pathways=selected_pathway)

def add_scores(count=0):
    """
    """
    with st.container(border=True):
        # Container divided into 2 columns, one for selecting and configuring columns and the other for displaying results 
        methods, result = st.columns([6, 9], gap="large")
        with methods:
            method_choice = st.multiselect("Criterion", 
                                            options=["sum_sd", "number_of_flux", "number_of_labeled_inputs", "price"],
                                            key=f"method_choice_{count}"
                                            )
            session.register_widgets({"method_choice": method_choice})

            if "sum_sd" in method_choice:
                weight_sd=st.text_input("Weight_sum_sd", 
                                        key=f"weight_Sds_{count}", 
                                        value=1)
                
            if "number_of_flux" in method_choice:
                weight_flux = st.text_input("Weight_flux",
                                            key=f"weight_flux_{count}", 
                                            value=1)
                input_threshold = st.text_input("Threshold", 
                                                    key=f"threshold_{count}", 
                                                    value=1)
                
            if "number_of_labeled_inputs" in method_choice:
                input_labeled_input=st.text_input("Weight_labeled_input", 
                                                key=f"weight_labeled_input_{count}", 
                                                value=1)
                
            # If more than one method is selected, the user can choose the operation to apply
            if len(method_choice) > 1:
                operation = st.selectbox("Operations", 
                                        options=["Addition", "Multiply", "Divide"],
                                        key=f"operation_{count}",
                                        index = None
                                        )

        submitted = st.button("Submit", 
                            key=f"submit_container_{count}")

        if submitted:
        # Generate the score based on the selected methods
            process_object.generate_score(method_choice,
                                        operation = operation if len(method_choice) > 1 else None,                         
                                        weight_sum_sd=int(weight_sd) if "sum_sd" in method_choice else 1,
                                            threshold=int(input_threshold) if "number_of_flux" in method_choice else 1,
                                            weight_flux=int(weight_flux) if "number_of_flux" in method_choice else 1,
                                            info_linp_files_dict=dict(process_object.linp_infos) if "number_of_labeled_inputs" or "price" in method_choice else None,
                                            weight_labeled_input=int(input_labeled_input) if "number_of_labeled_inputs" in method_choice else 1
                                        )
            session.register_widgets({"submit_container": submitted})
        
        if session.widget_space["submit_container"]:
            with result:     
                st.write("")
                dataframe, barplot = st.columns([10, 15])
                with dataframe:                          
                    table_score = st.dataframe(process_object.display_scores(),
                                on_select="rerun",
                                selection_mode="multi-row",
                                use_container_width=True,
                                key=f"table_score_{count}")
                    
                with barplot:
                    df=process_object.display_scores()
                    if table_score.selection.rows:
                        # Display the selected rows in a bar plot
                        df = process_object.display_scores().iloc[table_score.selection.rows,:]
                    
                    # Display the scores in a bar plot
                    fig = px.bar(df, x=df.index, y=df.columns, barmode="group")
                    st.plotly_chart(fig)
        
    add_score = st.button("Add score", key=f"add_score_{count}")
    if add_score:
        session.register_widgets({f"add_score_{count}": add_score})
    
    if session.widget_space[f"add_score_{count}"]:
        count += 1
        add_scores(count)

st.set_page_config(page_title="IsoDesign", layout="wide")
st.title("Analysis")

process_object = session.object_space['process_object']

summary_dataframe = process_object.summary_dataframe
filtered_dataframe = process_object.filtered_dataframe

# Display the simulation results dataframe
display_dataframe = st.dataframe(filtered_dataframe if filtered_dataframe is not None else summary_dataframe,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row")


with st.expander("**Apply a filter**"):
    st.write("Filter by : ")
    fluxes_name, kind, pathway = st.columns(3)
    with fluxes_name:
        selected_flux=st.multiselect(label="Fluxes_name", 
                                    options=filtered_dataframe["Name"].drop_duplicates() if filtered_dataframe is not None else summary_dataframe["Name"].drop_duplicates(), 
                                    label_visibility="collapsed",
                                    placeholder= "Flux")
        
    with kind:
        selected_kind=st.multiselect(label="kind", 
                                    options=["NET", "XCH", "METAB"], 
                                    label_visibility="collapsed", 
                                    placeholder="Kind")
    
    with pathway:
        selected_pathway=st.multiselect(label="Pathway", 
                                        options=process_object.netan["pathway"].keys() if process_object.netan["pathway"] else ["No pathway"], 
                                        label_visibility="collapsed", 
                                        placeholder="Pathway",
                                        disabled=True if not process_object.netan["pathway"] else False)
        

    submit=st.button("Submit",
                        on_click=filter,
                        args=(selected_flux, selected_kind, selected_pathway))

add_scores()


