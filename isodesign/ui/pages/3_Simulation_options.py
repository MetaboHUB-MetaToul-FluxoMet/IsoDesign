import streamlit as st
from sess_i.base.main import SessI
import streamlit.runtime.scriptrunner as scriptrunner
import concurrent.futures 

session = SessI(
        session_state=st.session_state,
        page="3_Simulation_options.py")


st.set_page_config(page_title="IsoDesign")
st.title("Simulation options")

st.sidebar.markdown("## Influx_si documentation ")
st.sidebar.link_button("Documentation", 
                       "https://influx-si.readthedocs.io/en/latest/index.html"
                  )
st.write(" ")

# Get the script run context
script_run_ctx = scriptrunner.get_script_run_ctx(suppress_warning=True)

process_object = session.object_space["process_object"]

def influx_sim():
    """
    Run the simulations in parallel with the selected mode.

    This function utilizes a ThreadPoolExecutor to run the influx_simulation
    method of the process_object in parallel. It also adds the script run 
    context to each thread in the executor.
    """
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_object.influx_simulation, mode)
        for processes in executor._threads:
            scriptrunner.add_script_run_ctx(processes, script_run_ctx)


if not process_object :
    st.warning("Please load a metabolic network model in 'Upload data' page.")

elif not process_object.isotopomers:
    st.warning("Please enter labelled substrates in 'Labels input' page.")
else:
    # Command to be passed to the simulation
    # The command is initialized with the prefix and default options
    command :list = ["--prefix", process_object.model_name, "--noopt"]   

    mode = st.selectbox("Influx mode", 
                        options=["influx_s", "influx_i"],
                        index=0,
                        help="Select the influx mode.\
                        \ninflux_s: stationary,\
                        \ninflux_i: instationary")
    session.register_widgets({"mode": mode})


    with st.container(border=True):
        emu = st.checkbox("Elementary Metabolite Units (EMU)", 
                        key="emu", 
                        value=True,
                        help="Use Elementary Metabolite Units (EMU) for the simulation")

        if emu == True:
            command.append("--emu")

        if mode == "influx_i":
            no_scale = st.checkbox("No scale", 
                                    key="--noscale", 
                                    value=True,
                                    help="Do not scale the fluxes")
            if no_scale:
                command.append("--noscale")

        ln = st.checkbox("Least norm solution (ln)", 
                        key="--ln", 
                        value=True,
                        help="Use the least norm solution (ln) for the simulation")
        if ln:
            command.append("--ln")

        add_options = st.text_input("Add options", 
                                    key="add_options")
        if add_options:
            command.append(f"--{add_options}")
   
    st.info(f"{len(process_object.labelled_substrates_combs)} combinations will be simulated.")
    st.info(f"Command to run: {command}")
    
    submit = st.button("Submit")
    if submit:
        process_object.command_list = command
        try:
            with st.spinner("Simulation in progress..."):
                influx_sim()
                process_object.generate_summary()
            st.success("Simulation completed ! ")
            st.switch_page(r"pages/4_Results_Analysis.py")
        except Exception as e:
            st.error(f"An error occured during the simulation : {e}")
            
        
        
        
