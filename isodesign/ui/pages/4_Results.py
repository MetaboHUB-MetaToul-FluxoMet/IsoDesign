import streamlit as st
from sess_i.base.main import SessI

#############
# FUNCTIONS #
#############

def display_dataframe(count):
    """
    This function displays the dataframe showing the results of the simulations. 
    It also provides the logic for filtering this dataframe.

    :param count: 
    """
    with st.expander("**Apply a filter**"):
        st.write("Filter by : ")
        fluxes_name, kind, pathway = st.columns(3, vertical_alignment="top")
        selected_flux=fluxes_name.multiselect(label="Fluxes_name", 
                                        options=process_object.summary_dataframe["Name"].drop_duplicates(), 
                                        label_visibility="collapsed",
                                        placeholder= "Flux",
                                        key=f"selected_flux_{count}")
        selected_kind=kind.multiselect(label="kind", 
                                        options=["NET", "XCH", "METAB"], 
                                        label_visibility="collapsed", 
                                        placeholder="Kind",
                                        key=f"selected_kind_{count}")
        
        selected_pathway=pathway.multiselect(label="Pathway", 
                                            options=process_object.netan["pathway"].keys() if process_object.netan["pathway"] else ["No pathway"], 
                                            label_visibility="collapsed", 
                                            placeholder="Pathway",
                                            disabled=True if not process_object.netan["pathway"] else False,
                                            key=f"selected_pathway_{count}") 
    
    # Dataframe filtering method
    process_object.data_filter(fluxes_names = selected_flux, 
                               kind = selected_kind, 
                               pathways=selected_pathway)
    
    # Display the simulation results dataframe
    st.dataframe(process_object.filtered_dataframe if process_object.filtered_dataframe is not None 
                                else process_object.summary_dataframe,
                            use_container_width=True,
                            hide_index=True,
                            on_select="rerun",
                            selection_mode="multi-row",
                            key=f"display_dataframe_{count}")

    session.register_widgets({f"dataframe_{count}": process_object.filtered_dataframe if process_object.filtered_dataframe is not None 
                                else process_object.summary_dataframe})


def criteria_block(count):
    """
    This function displays the various criteria 
    and associated results once applied (in the 
    form of a score table and barplot).

    :param count:
    """

    criteria, result = st.columns([6, 9], gap="large")
    with criteria:
        criteria = ["sum of SDs", "number of fluxes with SDs < threshold", "number of labeled inputs", "price"]
        method_choice = st.multiselect("Criteria", 
                                        options=criteria,
                                        key=f"method_choice_{count}")
        
        session.register_widgets({"method_choice": method_choice})

        if "sum of SDs" in method_choice:
            st.subheader("Sum of SDs")
            weight_sd=st.text_input("Weight", 
                                        key=f"weight_Sds_{count}", 
                                        value=1)
            
        if "number of fluxes with SDs < threshold" in method_choice:
            st.subheader("number of fluxes with SDs < threshold")
            weight_flux, input_threshold = st.columns(2, vertical_alignment="top")
            
            weight_flux = weight_flux.text_input("Weight",
                                key=f"weight_flux_{count}", 
                                value=1)
            
            input_threshold=input_threshold.text_input("Threshold", 
                                key=f"threshold_{count}", 
                                value=1)
            
        if "number of labeled inputs" in method_choice:
            st.subheader("Number of labeled inputs")
            input_labeled_input=st.text_input("Weight", 
                                            key=f"weight_labeled_input_{count}", 
                                            value=1)
            
        # If more than one method is selected, the user can choose the operation to apply
        if len(method_choice) > 1:
            operation = st.selectbox("Operations", 
                                    options=["Addition", "Multiply", "Divide"],
                                    key=f"operation_{count}",
                                    index = None)
        if method_choice:
            process_object.generate_score(method_choice,
                                            operation = operation if len(method_choice) > 1 else None,
                                            weight_sum_sd=float(weight_sd) if "sum of SDs" in method_choice else 1,
                                            threshold=float(input_threshold) if "number of fluxes with SDs < threshold" in method_choice else 1,
                                            weight_flux=float(weight_flux) if "number of fluxes with SDs < threshold" in method_choice else 1,
                                            info_linp_files_dict=dict(process_object.linp_infos) if "number of labeled inputs" or "price" in method_choice else None,
                                            weight_labeled_input=float(input_labeled_input) if "number of labeled inputs" in method_choice else 1)               
            
            with result:     
                logscale = st.checkbox("Apply a log", 
                                    key=f"logscale_{count}")
                if logscale:
                    process_object.apply_log()
                    
                dataframe, barplot = st.columns([10, 15])
                with dataframe:                       
                    table_score = st.dataframe(process_object.scores,
                                on_select="rerun",
                                selection_mode="multi-row",
                                use_container_width=True,
                                key=f"table_score_{count}")
                    # session.register_widgets({f"table_score_{count}": table_score})
                
                with barplot:
                    df = process_object.scores
                    if table_score.selection.rows:
                        # Display the selected rows in a bar plot
                        df = df.iloc[table_score.selection.rows,:]
                    session.register_widgets({f"table_{count}": df})
                    
                    process_object.draw_barplot(df)    
                    # Display the scores in a bar plot
                    st.plotly_chart(process_object.fig,
                                    key=f"barplot_{count}")
                    session.register_widgets({f"barplot_{count}": process_object.fig})

def new_scores(count=1):
    """
    This function generates a new score block. 
    It also provides the logic for exporting the data.
    """
    with st.container(border=False):
        st.header(f"Score {count}")
        display_dataframe(count)
        
        with st.container(border=True):
            criteria_block(count)

        process_object.register_scores(count,
                                       session.widget_space[f"table_{count}"],
                                       session.widget_space[f"barplot_{count}"])    

    new_score, export_data = st.columns([1, 9])
    
    with new_score:
        new_score_button= st.button("New score", 
                                    key=f"new_score_{count}")
        if new_score_button:
            session.register_widgets({f"new_score_{count}": new_score_button})

    with export_data:
        export_button = st.button("Export", key=f"export_{count}")  
    if export_button:
        with st.spinner("Exporting data ..."):
            process_object.export_data(f"score_{count}")
            st.success(f"Score {count} data exported successfully",)

    if session.widget_space[f"new_score_{count}"]:
        # If the user clicks on the "New score" button, a new score block is generated
        # and the count is incremented by 1
        st.divider()
        count += 1
        new_scores(count)

########
# MAIN #
########


st.set_page_config(page_title="IsoDesign", layout="wide")
st.title("Results")

session = SessI(
        session_state=st.session_state,
        page="4_Results")

process_object = session.object_space['process_object']

if not process_object:
    st.warning("Please load a metabolic network model in 'Upload data' page.")
elif process_object.summary_dataframe is None:
    st.warning("Please run the simulation in 'Simulation options' page.")
else:
    # Display the first score block.
    # It is a recursive function that will generate new score blocks 
    # if the user clicks on the "New score" button
    new_scores()
