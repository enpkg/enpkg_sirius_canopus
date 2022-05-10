# sirius_canopus

**Aim**: python script to lauch Sirius/ZODIAC/CSI-FingerID/CANOPUS + NPC Canopus on unaligned repositories.

Steps:
1. Download and install Sirius from [Sirius website](https://bio.informatik.uni-jena.de/software/sirius/). Make sure that you can use Sirius from your Terminal (for Windows, you will have to add sirius installation folder to you path).
2. Clone this repository
3. Create (<code>conda env create -f environment.yml</code>) and activate environment (<code>conda activate sirius_canopus_single_files</code>)
4. Adapt parameters in <code>/params/sirius_canopus_params.yml</code>, especially the path to the files you want to process (in the example below, it would be the path to "/data").<br>
Required structure for input data:
```
data
└─── sample_a
|       sample_a_metadata.tsv       # .tsv file with at least 1 column labeled 'sample_type' describing the sample type (either QC, blank or sample).
|       sample_a_sirius_pos.mgf     # .mgf file exported from MzMine2 containing spectra for Sirius
|
└─── sample_b
|
└─── sample_n
```
6. Launch the script: <code>python sirius_canopus_by_file.py</code><br>
NB: Sirius will be run only on files with "sample" datatype, not on QC, blanks or any other type.
