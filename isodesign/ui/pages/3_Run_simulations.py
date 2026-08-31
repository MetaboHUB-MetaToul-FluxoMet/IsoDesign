import streamlit as st
from sess_i.base.main import SessI
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx
import logging
import os

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

if "subprocess" not in st.session_state:
    st.session_state["subprocess"] = None

if "running" not in st.session_state:
    st.session_state.running = False

def check_err_files(tmp_folder):
    """ 
    Check if, at the end of calculations with influx_si, ".err" files are 
    empty. If they are not, return the file names and contents.
    """
    err_file_list = []
    for root, _ , files in os.walk(tmp_folder):
        for file in files:
            if file.endswith(".err"):
                # Check if the file is not empty
                if os.stat(os.path.join(root, file)).st_size > 0:
                    err_file_list.append(file)

        if err_file_list:
            for err_files in err_file_list:
                with open(os.path.join(root, err_files), 'r') as f:
                    err_file_content = f.read()
                    logger.error(f"Error file {err_files} - {err_file_content}")
                    raise Exception(f"Error file {err_files} - {err_file_content}")

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
        # Run the simulation
        st.session_state.subprocess = process_object.influx_simulation(param_list = command_list, 
                                        tmp_folder = io_object.tmp_folder_path)
        while True: 
            # Check if the subprocess is still running:
            if st.session_state.subprocess.poll() is not None :
                if st.session_state["subprocess"].returncode != 0 :
                    check_err_files(io_object.tmp_folder_path)
                    # Read the error message from the stderr file
                    stderr_output = st.session_state["subprocess"].stderr.read()
                    # Extract the last line of the error message to display it to the user
                    error_message = stderr_output.strip().split('\n')[-1]
                    logger.error(f"An error has occured during the simulation: {stderr_output}")
                    raise Exception(error_message)
                return
    except Exception as e:
        st.error(e)
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
    #TODO: check the interrupt simulation function
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


####### SIDEBAR ########
st.sidebar.markdown("## influx_si documentation ")
st.sidebar.link_button("Documentation", 
                       "https://influx-si.readthedocs.io/en/latest/manual.html"
                  )
####### SIDEBAR END ########

# Retrieving the process_object and io_object from the session's object space
process_object = session.object_space["process_object"]
io_object = session.object_space["io_object"]

if not process_object :
    st.warning("Please load a metabolic network model in 'Upload data' page.")

elif not process_object.linp_files_infos:
    # This warning appears if the user has not submitted the combinations generated on page 2 for simulation. 
    st.warning("Please click on the 'Validate inputs' button on the previous page.")
else:
    # Select the influx mode
    mode = st.selectbox("influx mode", 
                        options=["influx_s (stationary)", "influx_i (instationary)"],
                        index=0)
    
    session.register_widgets({"mode": mode})

    # Add the selected mode to the command list
    command_list = ["influx_s" if mode == "influx_s (stationary)" else "influx_i"] 

    # The command is initialized with the prefix and default options
    command_list += ["--prefix", io_object.model_name, "--noopt"]   

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
                # Clear the summary dataframe if it exists
                if process_object.summary_dataframe is not None:
                    process_object.summary_dataframe = None
                io_object.clear_previous_results()
                start_simulation()

                # Check if the subprocess has completed
                if st.session_state["subprocess"] :
                    if st.session_state["subprocess"].returncode == 0 :
                        process_object.configurate_summary(io_object.tmp_folder_path)
                        io_object.generate_summary(process_object.summary_dataframe)
                        to_pickle = {
                        "process_object":process_object,
                        "io_object": io_object}

                        process_object.save_process_to_file(to_pickle, io_object.results_dir_path, io_object.model_name)
                        # st.success("Simulation completed.")
        
                        st.success("Simulation completed.")
                        logger.info(f"Simulation with {mode} has been completed successfully.\n")
                        logger.info(f"Summary dataframe has been generated in {io_object.results_dir_path}.")
                        st.switch_page(r"pages/4_Analyze_results.py")

    with interrupt:
        # Interrupt simulation
        if st.button("Interrupt simulation", key="interrupt_simulation", on_click=interrupt_simulation) :
            logger.info("Simulation interrupted.")
            st.warning("Simulation interrupted.")
            
