import streamlit as st
import time
from sess_i.base.main import SessI
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx
import logging

logger = logging.getLogger("IsoDesign")

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

if "running" not in st.session_state:
    st.session_state.running = False

def execute_simulation():
    """
    Function to run simulations with influx_si. This function is run in 
    a separate thread to avoid blocking the Streamlit app.
    """
    # Attach Streamlit's runtime context to ensure thread compatibility
    ctx = st.runtime.scriptrunner.get_script_run_ctx()
    if ctx:
        add_script_run_ctx(st.session_state.th) #Thread.current_thread())
    try:
        st.session_state["subprocess"] = process_object.influx_simulation(command_list)
        while True:  
            # Check if the subprocess is still running
            if st.session_state["subprocess"].poll() is not None:
                if st.session_state["subprocess"].returncode != 0 :
                    process_object.check_err_files()
                    # Read the error message from the stderr file
                    stderr_output = st.session_state["subprocess"].stderr.read()
                    # Extract the last line of the error message to display it to the user
                    error_message = stderr_output.strip().split('\n')[-1]
                    logger.error(f"An error has occured during the simulation: {stderr_output}")
                    raise Exception(error_message)
                return
    except Exception as e:
        st.error(f"An error occured: {e}")
        return

def start_simulation():
    """
    Launch the simulation task in a separate thread and 
    wait for its completion. Ensures that the Streamlit 
    runtime context is properly attached to the thread.
    """
    st.session_state.running = True
    task_thread = Thread(target=execute_simulation)
    # Save the thread in session state
    st.session_state.th=task_thread
    # Attach the context to the thread
    add_script_run_ctx(task_thread)  
    task_thread.start()
    # Wait for the thread to complete before continuing
    task_thread.join()

def interrupt_simulation():
    """
    Interrupt simulations. This function is called when the user
    clicks the "Interrupt simulation" button.
    """
    st.session_state.running = False
    st.session_state["subprocess"].terminate()

########
# MAIN #
########

session = SessI(
        session_state=st.session_state,
        page="3_Run_simulations.py")


st.set_page_config(page_title="IsoDesign")
st.title("Run simulations")

st.sidebar.markdown("## Influx_si documentation ")
st.sidebar.link_button("Documentation", 
                       "https://influx-si.readthedocs.io/en/latest/manual.html"
                  )

process_object = session.object_space["process_object"]

if not process_object :
    st.warning("Please load a metabolic network model in 'Upload data' page.")

elif not process_object.linp_infos:
    # This warning appears if the user has not submitted the combinations generated on page 2 for simulation. 
    st.warning("Please click on the 'Submit for simulations' button on the previous page.")
else:
    # Select the influx mode
    mode = st.selectbox("Influx mode", 
                        options=["influx_s (stationary)", "influx_i (instationary)"],
                        index=0)
    
    session.register_widgets({"mode": mode})

    # Add the selected mode to the command list
    command_list = ["influx_s" if mode == "influx_s (stationary)" else "influx_i"] 

    # The command is initialized with the prefix and default options
    command_list += ["--prefix", process_object.model_name, "--noopt"]   

    with st.container(border=True):
        # Emu option
        emu = st.checkbox("Use EMU approach (--emu)", 
                        key="emu", 
                        value=True)
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
        ln = st.checkbox("Use least norm (--ln)", 
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
            st.subheader("Added option(s)")
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
    st.info(f"Command to run: {command_list}")

    submit, interrupt = st.columns([1, 1])
    with submit:
        if st.button("Start simulation", key="start_button"):
            with st.spinner("Simulating..."):
                # if there is a previous run, clear it
                process_object.clear_previous_results()
                # Clear the summary dataframe if it exists
                if process_object.summary_dataframe is not None:
                    process_object.summary_dataframe = None
                start_simulation()
                # Check if the subprocess has completed
                if st.session_state["subprocess"]:
                    if st.session_state["subprocess"].returncode == 0:
                        process_object.generate_summary()
                        process_object.save_process_to_file()
                        st.success("Simulation completed.")
                        logger.info(f"Simulation with {mode} has been completed successfully.\n")
                        logger.info(f"Summary dataframe has been generated in {process_object.output_folder_path}.")
                        st.switch_page(r"pages/4_Analyze_results.py")
        
    with interrupt:
        # Interrupt simulation
        if st.button("Interrupt simulation", key="interrupt_simulation", on_click=interrupt_simulation) :
            st.warning("Simulation interrupted.")
