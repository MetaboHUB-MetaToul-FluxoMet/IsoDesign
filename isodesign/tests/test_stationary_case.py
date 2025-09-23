from unittest.mock import patch, Mock
import pandas as pd
from isodesign.base.process import Process
import subprocess
import numpy as np

tvar_sim_file = {
    "ID_1": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.200000000000157, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),
    
    "ID_2":  pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.2, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),

    "ID_3": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.2000000000001, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),

    "ID_4": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.199992945204445, 0],
        "SD": [0.05, 0, 0.200000000000157, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),
    
    "ID_5": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.199901879566581, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),
    
    "ID_6": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.199901879566581, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),

    "ID_7": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.199901879566581, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),
    
    "ID_8": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.199863140933028, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]}),
    
    "ID_9": pd.DataFrame({
        "Id": [None, None, None, None],
        "Comment": [None, None, None, None],
        "Name": ["Gluc_in", "Gluc_in", "Arg_in", "Arg_in"],
        "Kind": ["NET", "XCH", "NET", "XCH"],
        "Type": ["F", "C", "F", "C"],
        "Value": [0.116481550597606, 0, 0.816481550597607, 0],
        "SD": [0.05, 0, 0.19984250885646, 0],
        "Struct_identif": ["yes", "yes", "yes", "yes"]})
}

def test_stationary_case(tmp_path):
    process = Process()
    process.get_netw_file_path(r"..\..\data\stationary_data\microfluxpCC25.netw")
    process.results_dir_path = tmp_path
    process.load_metabolic_netw_model()
    process.create_tmp_folder()
    process.model_analysis()
    important_key = ["input", "output", "pathway", "metabs", "Clen"]
    input_substrates = ["Gluc_out", "Arg_out", "Met_out", "Thr_out", "CO2_ext"]
    for key in important_key:
        assert key in process.netan.keys()
        assert key is not None
    for key in input_substrates:
        assert key in process.netan["input"]
    
    process.configure_unlabelled_form()
    process.add_isotopomer("Gluc_out", "100000", 2, 0, 1)
    process.add_isotopomer("Arg_out", "100000", 2, 0, 1)

    process.generate_combinations()

    process.configure_linp_files()
    process.generate_linp_files()
    process.generate_vmtf_file()

    ############################################
    # Influx simulation with mocked subprocess.Popen
    
    process._clear_previous_results = Mock()
    process._check_err_files = Mock()

    for id, dataframe in tvar_sim_file.items():
        dataframe.to_csv(process.tmp_folder_path / f"{id}.tvar.sim", sep="\t", index=False)

    # Patch os.chdir and subprocess.Popen
    with patch("os.chdir") as chdir_mock, \
        patch("subprocess.Popen") as popen_mock:
        # Mock the Popen instance
        proc_mock = Mock()
        proc_mock.communicate.return_value = ("", "")
        proc_mock.returncode = 0
        popen_mock.return_value = proc_mock

        param_list = ["influx_s", "--prefix", process.metabolic_netw_model_name, "--emu", "--ln", "--noopt"]
        process.influx_simulation(param_list)
        
        chdir_mock.assert_called_once_with(process.tmp_folder_path)
        popen_mock.assert_called_once_with(param_list, stderr=subprocess.PIPE, text=True)
        process._clear_previous_results.assert_called_with()
        process._check_err_files.assert_not_called()
        
    ##############################################
    process.generate_summary()
  
    process.filter_data(kind=["NET"])
    process.generate_score(["sum of SDs"])
    assert np.allclose(process.scores["sum of SDs"].tolist(), 
                       [0.25, 0.25, 0.25, 0.25, 0.2499, 0.2499, 0.2499, 0.2499, 0.2498], 
                       atol=1e-4)