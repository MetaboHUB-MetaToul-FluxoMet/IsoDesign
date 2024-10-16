import streamlit as st
from sess_i.base.main import SessI


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

process_object = session.object_space["process_object"]

# Command to be passed to the simulation
command :list = []   

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

    noopt = st.checkbox("No optmization (noopt)", 
                        key="--noopt", 
                        value=True,
                        help="Do not perform optimization")

    if noopt:
        command.append("--noopt")

    add_options = st.text_input("Add options", 
                                key="add_options")
    if add_options:
        command.append(f"--{add_options}")
    session.register_widgets({"--emu": emu,
                            "--noscale": no_scale,
                            "--ln": ln,
                            "add_options": add_options,
                            })

st.info(f"Selected options : {command}")

submit = st.button("Submit")
if submit:
    st.info("Simulation in progress...")
    process_object.influx_simulation(command, influx_mode=mode)
    st.success("Simulation completed ! ")
    
    process_object.generate_summary()
    st.switch_page(r"pages/4_Results_Analysis.py")

