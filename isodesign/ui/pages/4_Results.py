import streamlit as st
from sess_i.base.main import SessI
import plotly.io as pio
import plotly.express as px
from pathlib import Path

#############
# FUNCTIONS #
#############

def display_dataframe(count):
    """
    This function displays the dataframe showing the results of the simulations. 
    It also provides the logic for filtering this dataframe.

    :param count: number of the score 
    """
    
    with st.expander("**Apply a filter**"):
        st.write("Filter by : ")
        fluxes_name, kind, pathway = st.columns(3, vertical_alignment="top")
        
        # If a previous process has been imported via a pickle file, 
        # the filter values used previously are stored and displayed in the widget.
        if f"selected_flux_{count}" not in st.session_state:
            st.session_state[f"selected_flux_{count}"] = [] if count not in process_object.all_scores \
                else process_object.all_scores[count]["filters"]["fluxes_names"] 
        
        fluxes_name.multiselect(label="Fluxes_name", 
                                options=process_object.summary_dataframe["Name"].drop_duplicates(), 
                                label_visibility="collapsed",
                                placeholder= "Flux",
                                key=f"selected_flux_{count}")
                                        
        if f"selected_kind_{count}" not in st.session_state:
            st.session_state[f"selected_kind_{count}"] = [] if count not in process_object.all_scores \
                else process_object.all_scores[count]["filters"]["kind"] 
            
        kind.multiselect(label="kind", 
                        options=["NET", "XCH", "METAB"], 
                        label_visibility="collapsed", 
                        placeholder="Kind",
                        key=f"selected_kind_{count}")
                                
        if f"selected_pathway_{count}" not in st.session_state:
            st.session_state[f"selected_pathway_{count}"] = [] if count not in process_object.all_scores \
                else process_object.all_scores[count]["filters"]["pathways"] 
        
        pathway.multiselect(label="Pathway", 
                            options=process_object.netan["pathway"].keys() if process_object.netan["pathway"] else ["No pathway"], 
                            label_visibility="collapsed", 
                            placeholder="Pathway",
                            disabled=True if not process_object.netan["pathway"] else False,
                            key=f"selected_pathway_{count}") 

    # Uses the function to filter the table       
    process_object.data_filter(fluxes_names = st.session_state[f"selected_flux_{count}"], 
                               kind = st.session_state[f"selected_kind_{count}"], 
                               pathways=st.session_state[f"selected_pathway_{count}"])
    # if not "Select" in process_object.filtered_dataframe.columns:
    #     process_object.filtered_dataframe.insert(0, "Select", False)
    
    # Display the simulation results dataframe. The table is updated according to the filters used 
    st.dataframe(process_object.filtered_dataframe if process_object.filtered_dataframe is not None 
                    else process_object.summary_dataframe,
                use_container_width=True,
                hide_index=True,
                key=f"display_dataframe_{count}")
   
    # if not f'filtered_df_{count}' in st.session_state:
    #     st.session_state[f'filtered_df_{count}'] = None
    
    # df = st.data_editor(process_object.filtered_dataframe,
    #                 key=f"display_df_{count}",
    #                 hide_index=True)

    # st.session_state[f'filtered_df_{count}'] = df
    
    # process_object.filtered_dataframe = df


def criteria_block(count):
    """
    This function displays the various criteria 
    and associated results once applied (in the 
    form of a score table and barplot).

    :param count: number of the score 
    """

    criteria, result = st.columns([6, 9], gap="large")

    with criteria:
        criteria = ["sum of SDs", 
                    "number of fluxes with SDs < threshold", 
                    "number of labeled inputs", 
                    "number of structurally identified fluxes",
                    "price"]
        
        if f"method_choice_{count}" not in st.session_state:
            st.session_state[f"method_choice_{count}"] = [] if count not in process_object.all_scores \
                else process_object.all_scores[count]["criteria"]
        
        method_choice = st.multiselect("Criteria", 
                                        options=criteria,
                                        key=f"method_choice_{count}")

        if "sum of SDs" in method_choice:
            st.subheader("Sum of SDs")

            if f"weight_Sds_{count}" not in st.session_state:
                st.session_state[f"weight_Sds_{count}"] = 1 if not process_object.all_scores[count].get("criteria_parameters")\
                    else process_object.all_scores[count]["criteria_parameters"]["weight_sum_sd"]
            
            weight_sd=st.number_input("Weight", 
                                    key=f"weight_Sds_{count}", 
                                    min_value=1.0)
            
        if "number of fluxes with SDs < threshold" in method_choice:
            st.subheader("number of fluxes with SDs < threshold")
            weight_flux, input_threshold = st.columns(2, vertical_alignment="top")
            
            if f"weight_flux_{count}" not in st.session_state:
                st.session_state[f"weight_flux_{count}"] = 1 if not process_object.all_scores[count].get("criteria_parameters") \
                    else process_object.all_scores[count]["criteria_parameters"]["weight_flux"]

            weight_flux = weight_flux.number_input("Weight",
                                key=f"weight_flux_{count}")
            
            if f"threshold_{count}" not in st.session_state:
                st.session_state[f"threshold_{count}"] = 1 if not process_object.all_scores[count].get("criteria_parameters") \
                    else process_object.all_scores[count]["criteria_parameters"]["threshold"]

            input_threshold=input_threshold.number_input("Threshold", 
                                key=f"threshold_{count}")
            
        if "number of labeled inputs" in method_choice:
            st.subheader("Number of labeled inputs")
            
            if f"weight_labeled_input_{count}" not in st.session_state:
                st.session_state[f"weight_labeled_input_{count}"] = 1 if not process_object.all_scores[count].get("criteria_parameters") \
                    else process_object.all_scores[count]["criteria_parameters"]["weight_labeled_input"]
            
            input_labeled_input=st.number_input("Weight", 
                                                key=f"weight_labeled_input_{count}")
        
        if "number of structurally identified fluxes" in method_choice:
            st.subheader("Number of structurally identified fluxes")
            if f"weight_struct_identif_{count}" not in st.session_state:
                st.session_state[f"weight_struct_identif_{count}"] = 1 if not process_object.all_scores[count].get("criteria_parameters") \
                    else process_object.all_scores[count]["criteria_parameters"]["weight_struct_identif"]
            
            input_struct_identif=st.number_input("Weight", 
                                                key=f"weight_struct_identif_{count}")
            
        # If more than one method is selected, the user can choose the operation to apply
        if len(method_choice) > 1:
            if f"operation_{count}" not in st.session_state:
                st.session_state[f"operation_{count}"] = None if count not in process_object.all_scores \
                    else process_object.all_scores[count]["applied_operations"]
                
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
                                          weight_labeled_input=float(input_labeled_input) if "number of labeled inputs" in method_choice else 1,
                                          struct_identif_dict=dict(process_object.structures_identified) if "number of structurally identified fluxes" in method_choice else None,
                                          weight_struct_identif=float(input_struct_identif) if "number of structurally identified fluxes" in method_choice else 1)
            
            with result:     
                logscale = st.checkbox("Log scale", 
                                        key=f"logscale_{count}")
                if logscale:
                    process_object.apply_log()
                    
                table_score, barplot = st.columns([10, 15])

                with table_score:                       
                    table = st.dataframe(process_object.scores,
                                on_select="rerun",
                                selection_mode="multi-row",
                                use_container_width=True,
                                key=f"table_score_{count}")
                                    
                with barplot:
                    df_for_barplot = process_object.scores
                    if table.selection.rows:
                        # Display the selected rows in a bar plot
                        df_for_barplot = df_for_barplot.iloc[table.selection.rows,:]
                    
                    # Set the default template to plotly
                    pio.templates.default = "plotly"

                    if  f"fig_{count}" not in st.session_state:
                        st.session_state[f"fig_{count}"] = None
                    
                    # The color_discrete_sequence is used to define a specific set of colors for the bars in the plot.
                    # This is particularly useful when integrating with Streamlit, 
                    # as it ensures consistent color usage across different plots.
                    fig = px.bar(df_for_barplot,
                                x=df_for_barplot.index,
                                y=df_for_barplot.columns,
                                barmode='group',
                                color_discrete_sequence=[
                                    "#0068c9",
                                    "#83c9ff",
                                    "#ff2b2b",
                                    "#ffabab",
                                    "#29b09d",
                                    "#7defa1",
                                    "#ff8700",
                                    "#ffd16a",
                                    "#6d3fc0",
                                    "#d5dae5",
                                ])
                    # Update the legend position
                    fig.update_layout(legend = dict(
                        title="Criteria",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
                    # Update the fig in the session state
                    st.session_state[f"fig_{count}"] = fig
                    # Display the figure in the Streamlit app
                    st.plotly_chart(fig, 
                                    key=f"barplot_{count}")


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
    # Checks if the "scores" key does not exist in st.session_state. If it does not exist, 
    # it is initialised with [1] if process_object.all_scores is empty (no pickle file imported), 
    # otherwise it is filled with the values from process_object.all_scores in the form of a list.   
    if "scores" not in st.session_state:
        st.session_state["scores"] = [1] if not process_object.all_scores else list(process_object.all_scores)

    # A "score" block is created for each number in the list.
    for count in st.session_state["scores"]:
        # Stock, in the session state, of the st.text_input key in which the new name will be entered 
        if f"name_change_{count}" not in st.session_state:
            st.session_state[f"name_change_{count}"] = None
        # Store header name in session state
        # If the header name does not exist in the session state, it is initialized with “Score {count}” 
        # If a pickle file has been imported, it takes the name stored in the pickle file. 
        if f"header_{count}" not in st.session_state:
            st.session_state[f"header_{count}"] = f"Score {count}" if count not in process_object.all_scores \
                else process_object.all_scores[count]["name"]
        # If a new name has been entered in the st.text_input, it is stored in the session state.
        if st.session_state[f"name_change_{count}"]:
            st.session_state[f"header_{count}"] = st.session_state[f"name_change_{count}"]
        
        pen_button, header  = st.columns(spec=[0.05,0.95])    
        with pen_button:
            st.write(" ")
            pen_button = st.button(":pencil2:", 
                                    key=f"pen_button_{count}")
            
        with header:
            st.header(st.session_state[f"header_{count}"])
        
        
        if pen_button:
            st.text_input("Change the name",
                        key=f"name_change_{count}")
            
        display_dataframe(count)
    
        with st.container(border=True):
            criteria_block(count)
        
        new_score, export_data = st.columns([1, 9])
        
        with new_score:
            new_score_button= st.button("New score", 
                                            key=f"new_score_button_{count}")
            
        # If the "new_score_button" is activated, the maximum of the existing scores 
        # in st.session_state["scores"] is taken and incremented by 1
        # to determine the next value of the "score" block to be added. 
        if new_score_button:
            new_count = max(st.session_state["scores"]) + 1  
            st.session_state["scores"].append(new_count)

        with export_data:
            export_button = st.button("Export", key=f"export_{count}") 

        if export_button:
            with st.spinner("Exporting data ..."):
                res_folder_path = Path(f"{process_object.output_folder_path}/Score_{count}_res")
                res_folder_path.mkdir(parents=True, exist_ok=True)
                # Export the dataframe and the scores table to an Excel file
                process_object.all_scores[count]["dataframe"].to_excel(f"{res_folder_path}/{count}_dataframe.xlsx", index=False)
                # st.session_state[f"filtered_df_{count}"].to_excel(f"{res_folder_path}/{count}_dataframe.xlsx", index=False)
                process_object.all_scores[count]["columns_scores"].to_excel(f"{res_folder_path}/{count}_scores_table.xlsx", index=True)
                # Export the barplot to an HTML file
                st.session_state[f"fig_{count}"].write_html(f"{res_folder_path}/{count}_barplot.html")
                st.success(f"Score {count} data exported successfully")
        # Save the "score" block to the process_object and save it to a pickle file
        process_object.register_scores(count, block_name=st.session_state[f"header_{count}"])
        process_object.save_process_to_file()
