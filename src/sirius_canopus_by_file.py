import os
import yaml
from pathlib import Path
import pandas as pd
import subprocess
import shutil

my_env = os.environ.copy()
# my_env["GUROBI_HOME"] = "/prog/gurobi951/linux64/"

p = Path(__file__).parents[1]
os.chdir(p)
from canopus import Canopus

with open (r'configs/user/user.yml') as file:    
    params_list = yaml.load(file, Loader=yaml.FullLoader)

path_to_data = params_list['paths'][0]['path_to_data']

sirius_version = params_list['options'][0]['sirius_version']
ioniziation = params_list['options'][1]['ioniziation']
sirius_command = params_list['options'][2]['sirius_command']
recompute = params_list['options'][3]['recompute']
zip_output = params_list['options'][4]['zip_output']

output_suffix = 'WORKSPACE_SIRIUS'
    
# Lauch sirius+ canopus job on a file
def compute_sirius_canopus(file, output_name):
    subprocess.run(sirius_command.format(file=file, output_name=output_name))
                      
path = os.path.normpath(path_to_data)
samples_dir = [directory for directory in os.listdir(path)]

for directory in samples_dir:
    metadata_path = os.path.join(path, directory, directory + '_metadata.tsv')
    try:
        metadata = pd.read_csv(metadata_path, sep='\t')
    except FileNotFoundError:
        continue
    except NotADirectoryError:
        continue
    # Check if the sample type is sample and not QC or Blank
    if metadata['sample_type'][0] == 'sample':
        if ioniziation == 'pos':    
            sirius_mgf_path = os.path.join(path, directory,ioniziation, directory + '_sirius_pos.mgf')
        elif ioniziation == 'neg':    
            sirius_mgf_path = os.path.join(path, directory,ioniziation, directory + '_sirius_neg.mgf')
        else:
            raise ValueError("ioniziation parameter must be pos or neg")   
           
        output_folder = os.path.join(path, directory, ioniziation, directory + '_' + output_suffix)        
        if (recompute is False) & (os.path.isdir(output_folder)):
            print(f"Skipped already computed sample: {directory}")          
            continue
        else:
            if os.path.isdir(output_folder):
                shutil.rmtree(output_folder)
            
            if sirius_version == 4:
                print(f"Computing Sirius on sample: {directory}")
                compute_sirius_canopus(sirius_mgf_path, output_folder)
                print(f"Computing NPC Canopus on sample: {directory}")            
                C = Canopus(sirius=output_folder)
                C.npcSummary().to_csv(os.path.join(output_folder, "npc_summary.csv"))            
                print(f"Zipping outputs on sample: {directory}")
                
            elif sirius_version == 5:
                print(f"Computing Sirius on sample: {directory}")
                compute_sirius_canopus(sirius_mgf_path, output_folder)
            else:
                raise ValueError("sirius_version parameter must be 4 or 5")
            
            if zip_output:
                for dir in [directory for directory in os.listdir(output_folder)]:
                    if os.path.isdir(os.path.join(output_folder, dir)):
                        shutil.make_archive(os.path.join(output_folder, dir), 'zip', os.path.join(output_folder, dir))
                        shutil.rmtree(os.path.join(output_folder, dir))
                          
            shutil.copyfile(r'configs/user/user.yml', os.path.join(path, directory, ioniziation, directory + '_' + output_suffix, 'params.yml'))
            
            print(f"Sample: {directory} done")
                
