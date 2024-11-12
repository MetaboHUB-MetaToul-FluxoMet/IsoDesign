import streamlit as st
from sess_i.base.main import SessI


#############
# FUNCTIONS #
#############

def clear_text_input():
    """ 
    Clear the "add_options" widget (st.text_input 
    widget) once the option has been added. 
    """
    # Save the option in the SessI before clearing the widget from the session state
    session.register_widgets({"add_options": st.session_state["add_options_text_input"]}) 
    st.session_state["add_options_text_input"] = ""

def delete_option(option):
    """
    Delete an option from the list of added options.
    """
    session.widget_space["list_added_options"].remove(option)
    process_object.command_list.remove(f"--{option}")    


########
# MAIN #
########

session = SessI(
        session_state=st.session_state,
        page="3_Simulation_options.py")


st.set_page_config(page_title="IsoDesign")
st.title("Simulation options")

st.sidebar.markdown("## Influx_si documentation ")
st.sidebar.link_button("Documentation", 
                       "https://influx-si.readthedocs.io/en/latest/index.html"
                  )

process_object = session.object_space["process_object"]

if not process_object :
    st.warning("Please load a metabolic network model in 'Upload data' page.")

elif not process_object.isotopomers:
    st.warning("Please enter labelled substrates in 'Labels input' page.")
else:
    # Command to be passed to the simulation
    # The command is initialized with the prefix and default options
    process_object.command_list = ["--prefix", process_object.model_name, "--noopt"]   

    # Select the influx mode
    mode = st.selectbox("Influx mode", 
                        options=["influx_s", "influx_i"],
                        index=0,
                        help="Select the influx mode.\
                        \ninflux_s: stationary,\
                        \ninflux_i: instationary")
    session.register_widgets({"mode": mode})


    with st.container(border=True):
        # Emu option
        emu = st.checkbox("Elementary Metabolite Units (EMU)", 
                        key="emu", 
                        value=True,
                        help="Use Elementary Metabolite Units (EMU) for the simulation")
        session.register_widgets({"emu": emu})
        
        if emu == True:
            process_object.command_list.append("--emu")
        
        # No scale option only if influx_i mode
        if mode == "influx_i":
            no_scale = st.checkbox("No scale", 
                                    key="--noscale", 
                                    value=True)
            session.register_widgets({"no_scale": no_scale})
            
            if no_scale:
                process_object.command_list.append("--noscale")

        # Least norm solution option
        ln = st.checkbox("Least norm solution (ln)", 
                        key="--ln", 
                        value=True)
        
        session.register_widgets({"ln": ln})
        
        if ln:
            process_object.command_list.append("--ln")

        # Add options manually 
        add_options = st.text_input("Add options", 
                                    key="add_options_text_input")

        add = st.button("Add",
                        key="add_button",
                        on_click=clear_text_input)
        
        session.register_widgets({"add": add})

        if session.widget_space["add"]:
            # Create a list (if there isn't one) to store the options added to the SessI widgets
            if not session.widget_space["list_added_options"]:
                session.register_widgets({"list_added_options": [session.widget_space["add_options"]]})
            # Check if the option is already added
            elif session.widget_space["add_options"] in session.widget_space["list_added_options"]:
                st.warning("Option already added.")
            else:
                session.widget_space["list_added_options"].append(session.widget_space["add_options"])
            
        if session.widget_space["list_added_options"]:
            st.subheader("Added options")
            for option in session.widget_space["list_added_options"]:
                # Add the option to the command list
                process_object.command_list.append(f"--{option}")
                show_options, deletion = st.columns([0.05, 0.1])
                with show_options:
                    st.info(option)
                with deletion:
                    delete = st.button(label=":x:", 
                                            key=f"delete_{option}",
                                            on_click=delete_option,
                                            args=(option,))

    st.info(f"{len(process_object.linp_dataframes)} combinations will be simulated.")
    st.info(f"Command to run: {process_object.command_list}")
    
    submit = st.button("Submit")

    if submit:
        with st.spinner("Simulation in progress..."):
            process_object.influx_simulation(mode)
            process_object.generate_summary()
            process_object.save_process_to_file()
            st.success("Simulation completed ! ")
        st.switch_page(r"pages/4_Results_Analysis.py")
        
        
        
        
