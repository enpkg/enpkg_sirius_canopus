import os
import yaml
from pathlib import Path
import pandas as pd
import subprocess
import shutil
from canopus import Canopus

my_env = os.environ.copy()
# my_env["GUROBI_HOME"] = "/prog/gurobi951/linux64/"

p = Path(__file__).parents[0]
os.chdir(p)
print(p)

with open (r'params/sirius_canopus_params.yml') as file:    
    params_list = yaml.load(file, Loader=yaml.FullLoader)

path_to_data = params_list['paths'][0]['path_to_data']

sirius_version = params_list['options'][0]['sirius_version']
ioniziation = params_list['options'][1]['ioniziation']
sirius_command = params_list['options'][2]['sirius_command']
output_suffix = params_list['options'][3]['output_suffix']
recompute = params_list['options'][4]['recompute']
zip_output = params_list['options'][5]['zip_output']

        
# Lauch sirius+ canopus job on a file
def compute_sirius_canopus(file, output_name):
    subprocess.run(sirius_command.format(file=file, output_name=output_name))
 #--processors 40 

# def compute_sirius5_canopus(file, output_name):
#     subprocess.run(f"/prog/sirius/bin/sirius -i {file} --output {output_name} \
#     --maxmz 800 \
#     config --IsotopeSettings.filter true --FormulaSearchDB BIO --Timeout.secondsPerTree 300 --FormulaSettings.enforced HCNOP --Timeout.secondsPerInstance 300 \
#     --AdductSettings.detectable '[[M + H]+, [M - H4O2 + H]+, [M - H2O + H]+, [M + Na]+, [M + H3N + H]+, [M + K]+]' --UseHeuristic.mzToUseHeuristicOnly 650 \
#         --AlgorithmProfile orbitrap --IsotopeMs2Settings SCORE --MS2MassDeviation.allowedMassDeviation 5.0ppm --NumberOfCandidatesPerIon 1 --UseHeuristic.mzToUseHeuristic 300\
#             --FormulaSettings.detectable B,Cl,Br,Se,S --NumberOfCandidates 10 --ZodiacNumberOfConsideredCandidatesAt300Mz 10 --ZodiacRunInTwoSteps true \
#                 --ZodiacEdgeFilterThresholds.minLocalConnections 10 --ZodiacEdgeFilterThresholds.thresholdFilter 0.95 --ZodiacEpochs.burnInPeriod 2000 \
#                     --ZodiacEpochs.numberOfMarkovChains 10 --ZodiacNumberOfConsideredCandidatesAt800Mz 50 --ZodiacEpochs.iterations 20000 \
#                         --AdductSettings.enforced , --AdductSettings.fallback '[[M + H]+, [ M + Na]+, [M + K]+]' --FormulaResultThreshold true --InjectElGordoCompounds true \
#                             --StructureSearchDB BIO --RecomputeResults false formula zodiac fingerprint structure canopus", shell=True, env=my_env)

# def compute_sirius5_canopus(file, output_name):
#     subprocess.run(f"sirius -i {file} --output {output_name} --maxmz 800 formula --ppm-max 10 \
#         --profile orbitrap --candidates 10 --tree-timeout 50 --compound-timeout 500 --ions-considered [M+H3N+H]+,[M+H]+,[M+K]+,[M+Na]+,[M+NH4]+\
#         --ionsEnforced [M + H]+ zodiac fingerprint structure --db bio canopus write-summaries --output {output_name}")
    
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
                          
            shutil.copyfile(r'params/sirius_canopus_params.yml', os.path.join(path, directory, ioniziation, directory + '_' + output_suffix, 'params.yml'))
            
            print(f"Sample: {directory} done")
                
