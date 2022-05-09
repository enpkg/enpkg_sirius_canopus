import os
import yaml
from pathlib import Path
import pandas as pd
import subprocess
import shutil
from canopus import Canopus

p = Path(__file__).parents[0]
os.chdir(p)

with open (r'params/sirius_canopus_params.yml') as file:    
    params_list = yaml.load(file, Loader=yaml.FullLoader)

path_to_data = params_list['paths'][0]['path_to_data']

output_suffix = params_list['options'][0]['output_suffix']
recompute = params_list['options'][1]['recompute']
zip_output = params_list['options'][2]['zip_output']

# Lauch sirius+ canopus job on a file
def compute_sirius_canopus(file, output_name):
    subprocess.run(f"sirius -i {file} --output {output_name} --maxmz 800 formula --ppm-max 10 \
        --profile orbitrap --candidates 10 --tree-timeout 50 --compound-timeout 500 --ions-considered [M+H3N+H]+,[M+H]+,[M+K]+,[M+Na]+,[M+NH4]+\
        --ions-enforced [M+H]+ zodiac structure --database bio canopus")
 #--processors 40 
 
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
        sirius_mgf_path = os.path.join(path, directory,directory + '_sirius_pos.mgf')      
        output_folder = os.path.join(path, directory,directory + '_' + output_suffix)        
        if (recompute is False) & (os.path.isdir(output_folder)):
            print(f"Skipped already computed sample: {directory}")          
            continue
        else:
            if os.path.isdir(output_folder):
                shutil.rmtree(output_folder)
                            
            print(f"Computing Sirius on sample: {directory}")            
            
            compute_sirius_canopus(sirius_mgf_path, output_folder)
            
            print(f"Computing NPC Canopus on sample: {directory}")
            
            C = Canopus(sirius=output_folder)
            C.npcSummary().to_csv(os.path.join(output_folder, "npc_summary.csv"))
            
            print(f"Zipping outputs on sample: {directory}")
            
            if zip_output:
                for dir in [directory for directory in os.listdir(output_folder)]:
                    if os.path.isdir(os.path.join(output_folder, dir)):
                        shutil.make_archive(os.path.join(output_folder, dir), 'zip', os.path.join(output_folder, dir))
                        shutil.rmtree(os.path.join(output_folder, dir))                    
            
            print(f"Sample: {directory} done")
                
