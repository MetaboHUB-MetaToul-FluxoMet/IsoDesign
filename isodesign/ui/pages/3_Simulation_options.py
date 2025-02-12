import streamlit as st
import signal, time
from sess_i.base.main import SessI
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx


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
    command_list.remove(f"{option}")    

if "suprocess" not in st.session_state:
    st.session_state["subprocess"] = None

def execute_simulation():
    """
    Execute the simulation task. 
    """
    # Attach Streamlit's runtime context to ensure thread compatibility
    ctx = st.runtime.scriptrunner.get_script_run_ctx()
    if ctx:
        add_script_run_ctx(st.session_state.th) #Thread.current_thread())
    try:
        subp=process_object.influx_simulation(command_list, mode)
        st.session_state["subprocess"] = subp
        if st.session_state.interrupt_button:
            # Interrupt the simulation
            subp.send_signal(signal.SIGINT)
    except Exception as e:
        st.error(f"An error occured: {e}")
        return

def start_simulation():
    """
    Launch the simulation task in a separate thread and 
    wait for its completion. Ensures that the Streamlit 
    runtime context is properly attached to the thread.
    """
    task_thread = Thread(target=execute_simulation)
    # Save the thread in session state
    st.session_state.th=task_thread
    # Attach the context to the thread
    add_script_run_ctx(task_thread)  
    task_thread.start()
    # Wait for the thread to complete before continuing
    task_thread.join()


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

elif not process_object.linp_infos:
    # This warning appears if the user has not submitted the combinations generated on page 2 for simulation. 
    st.warning("Please click on the 'Submit for simulations' button on the previous page.")
else:
    # Command to be passed to the simulation
    # The command is initialized with the prefix and default options
    command_list = ["--prefix", process_object.model_name, "--noopt"]   
    command_list = list(dict.fromkeys(command_list))

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
        emu = st.checkbox("Use emu approach", 
                        key="emu", 
                        value=True,
                        help="Use Elementary Metabolite Units (EMU) for the simulation")
        session.register_widgets({"emu": emu})
        
        if emu == True:
            command_list.append("--emu")
        
        # No scale option only if influx_i mode
        if mode == "influx_i":
            no_scale = st.checkbox("No scale", 
                                    key="--noscale", 
                                    value=True)
            session.register_widgets({"no_scale": no_scale})
            
            if no_scale:
                command_list.append("--noscale")

        # Least norm solution option
        ln = st.checkbox("Apply ln step", 
                        key="--ln", 
                        value=True)
        
        session.register_widgets({"ln": ln})
        
        if ln:
            command_list.append("--ln")

        # Add options manually 
        add_options = st.text_input("Add option", 
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
            st.subheader("Added option")
            for option in session.widget_space["list_added_options"]:
                # Add the option to the command list
                command_list.append(f"{option}")
                show_options, deletion = st.columns([0.05, 0.1])
                with show_options:
                    st.info(option)
                with deletion:
                    delete = st.button(label=":x:", 
                                            key=f"delete_{option}",
                                            on_click=delete_option,
                                            args=(option,))

    st.info(f"{len(process_object.linp_dataframes)} combinations will be simulated.")
    st.info(f"Command to run: {[mode] + command_list}")

    submit, interrupt = st.columns([1, 1])
    with submit:
        if st.button("Start simulation", key="start_button"):
            with st.spinner("Simulating..."):
                # if there is a previous run, clear it
                process_object.clear_previous_run()
                start_simulation()
                # Check if the subprocess has completed
                if st.session_state["subprocess"]:
                    if st.session_state["subprocess"].returncode == 0:
                        process_object.generate_summary()
                        process_object.save_process_to_file()
                        st.success("Simulation completed.")
                        st.switch_page(r"pages/4_Results.py")
        
    with interrupt:
        # Interrupt simulation
        if st.button("Interrupt simulation", key="interrupt_button"):
            st.warning("Simulation interrupted.")
           
        