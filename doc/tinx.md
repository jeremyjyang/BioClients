# `bioclients.tinx`

## TINX

TINX = Target Importance and Novelty Explorer

Developed by and for the Illuminating the Druggable Genome (IDG) 
Knowledge Management Center (KMC).

 * [TIN-X: target importance and novelty explorer](https://academic.oup.com/bioinformatics/article/33/16/2601/3111842), DC Cannon, JJ Yang, SL Mathias, O Ursu, S Mani, A Waller, SC Schürer, LJ Jensen, LA Sklar, CG Bologa, TI Oprea, Bioinformatics, 2017.
 * [TIN-X version 3: update with expanded dataset and modernized architecture for enhanced illumination of understudied targets](https://peerj.com/articles/17470/), VT Metzger, DC Cannon, JJ Yang, SL Mathias, CG Bologa, A Waller, SC Schürer, D Vidović, KJ Kelleher, TK Sheils, LJ Jensen, CG Lambert, TI Oprea, JS Edwards, PeerJ, 2024. 


### Usage

```
python3 -m bioclients.tinx.Client -h
usage: Client.py [-h] [--ids_disease IDS_DISEASE] [--ids_target IDS_TARGET]
                 [--ifile_disease IFILE_DISEASE] [--ifile_target IFILE_TARGET]
                 [--o OFILE] [--n_max_hit N_MAX_HIT] [--query SEARCH_QUERY]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {get_disease_targets,get_target_diseases,get_disease_target_publications,search_diseases,search_targets}

TINX REST API query client

positional arguments:
  {get_disease_targets,get_target_diseases,get_disease_target_publications,search_diseases,search_targets}
                        operation

options:
  -h, --help            show this help message and exit
  --ids_disease IDS_DISEASE
                        IDs, comma-separated (DOIDs for diseases)
  --ids_target IDS_TARGET
                        IDs, comma-separated (TINX_IDs for targets)
  --ifile_disease IFILE_DISEASE
                        input file, DOIDs
  --ifile_target IFILE_TARGET
                        input file, TINX_IDs
  --o OFILE             output (TSV)
  --n_max_hit N_MAX_HIT
                        max hits per query ID
  --query SEARCH_QUERY  search query
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example IDs: Diseases: DOID:0014667 Targets: 488
```
