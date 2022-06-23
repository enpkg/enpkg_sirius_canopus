# sirius_canopus
Python script to lauch Sirius/ZODIAC/CSI-FingerID/CANOPUS + NPC Canopus on unaligned repositories.  

⚙️ Workflow part of [enpkg_workflow](https://github.com/mandelbrot-project/enpkg_workflow).  

## Required starting architecture
```
data/
└─── sample_a/
|    └─── sample_a_metadata.tsv              
|    └─── pos/
|             sample_a_sirius_pos.mgf    
|    └─── neg/
|             sample_a_sirius_neg.mgf 
|
└─── sample_b/
|
└─── sample_n/
```

## 1. Download and install Sirius
Download and install Sirius from [Sirius website](https://bio.informatik.uni-jena.de/software/sirius/). Make sure that you can use Sirius from your Terminal (for Windows, you will have to add sirius installation folder to your [PATH](https://docs.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14))).

## Sirius 4 only: install canopus_treemap
For Sirius 4 only, install  https://github.com/kaibioinfo/canopus_treemap to have the NPClassifier classes from Canopus analysis. 

## 2. Clone repository and install environment

1. Clone this repository.
2. Create environment: 
```console 
conda env create -f environment.yml
```
3. Activate environment:  
```console 
conda activate sirius_canopus_single_files
```

## 3. Adapt parameters and launch the process! 🚀

1. Copy and rename the parameters file <code>../indifiles_annotation/configs/default/default.yml</code> into <code>../indifiles_annotation/configs/user/user.yml</code>
2. Modifiy the user.yaml file according to your needs (especially the paths).
3. Launch the script:
```console 
python src/sirius_canopus_by_file.py
```
NB: Sirius will be run only on files with "sample" datatype, not on QC, blanks or any other type.

##  Target architecture (for positive mode)

```
data/
└─── sample_a/
|     └───  sample_a_metadata.tsv
|     └─── pos/
|           └─── sample_a_sirius_pos.mgf
|           └─── sample_a_WORKSPACE_SIRIUS/
|                └─── 0_sample_a_sirius_pos_1.zip                                             # Feature's individual Sirius outputs
|                └─── ...
|                └─── canopus_compound_summary.tsv (Sirius 5) OR npc_summary.csv (Sirius 4)   # NPClassifier Canopus summary
|                └─── formula_identifications.tsv                                             # Sirius/Zodiac formula summary
|                └─── compound_identifications.tsv                                            # CSI:FingerID compound identification summary
|                └─── ...
└─── sample_b/
|
└─── sample_n/
```


