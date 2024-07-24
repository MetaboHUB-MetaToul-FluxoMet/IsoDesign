import streamlit as st
from sess_i.base.main import SessI

session = SessI(
        session_state=st.session_state,
        page="3_Simulation_options.py")


st.set_page_config(page_title="IsoDesign")
st.title("Simulation options")

st.write(" ")

param_list=[]
feasability_domain = st.checkbox("Feasibility domain projection",
                                 help="Project the feasibility domain of the model")


emu = st.checkbox("Elementary Metabolite Units (EMU)", 
                  key="emu", 
                  value=True,
                  help="Use Elementary Metabolite Units (EMU) for the simulation")

if emu == True:
    param_list.append("--emu")


no_scale = st.checkbox("No scale", 
                       key="--noscale", 
                       value=True,
                       help="Do not scale the fluxes")
if no_scale:
    param_list.append("--noscale")

ln = st.checkbox("Least norm solution (ln)", 
                 key="--ln", 
                 value=True,
                 help="Use the least norm solution (ln) for the simulation")
if ln:
    param_list.append("--ln")

noopt = st.checkbox("No optmization (noopt)", 
                    key="--noopt", 
                    value=True,
                    help="Do not perform optimization")

if noopt:
    param_list.append("--noopt")

add_options = st.text_input("Add options", 
                            key="add_options")
if add_options:
    param_list.append(f"--{add_options}")

session.register_widgets({"--emu": emu,
                          "--noscale": no_scale,
                          "--ln": ln,
                          "add_options": add_options,
                          "feasability_domain": feasability_domain})


submit = st.button("Submit")
if submit:
    session.object_space["process_object"].influx_simulation(param_list)
    session.object_space["process_object"].generate_summary()
    st.switch_page(r"pages/4_Analysis.py")
