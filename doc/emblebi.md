# `BioClients.emblebi`

## EMBL-EBI

Tools for obtaining and processing data from EMBL-EBI resources.
Some EMBL-EBI resources have separate BioClients modules.

* <https://www.ebi.ac.uk/>

### Identifiers

* <https://identifiers.org>
* <https://docs.identifiers.org/articles/api.html>

Examples:

```
$ python3 -m BioClients.emblebi.identifiers.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--query QUERY]
                 [--resolver_api_host RESOLVER_API_HOST]
                 [--resolver_api_base_path RESOLVER_API_BASE_PATH]
                 [--registry_api_host REGISTRY_API_HOST]
                 [--registry_api_base_path REGISTRY_API_BASE_PATH]
                 [--search_logic {containing,exact}] [-v]
                 {resolve,list_namespaces,list_resources,list_institutions,search_namespaces,search_institutions,search_resources}

EMBL-EBI Identifiers.org client

positional arguments:
  {resolve,list_namespaces,list_resources,list_institutions,search_namespaces,search_institutions,search_resources}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             Input IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input IDs (comma-separated)
  --query QUERY         Search query.
  --resolver_api_host RESOLVER_API_HOST
  --resolver_api_base_path RESOLVER_API_BASE_PATH
  --registry_api_host REGISTRY_API_HOST
  --registry_api_base_path REGISTRY_API_BASE_PATH
  --search_logic {containing,exact}
  -v, --verbose

Example IDs: taxonomy:9606
```

### Unichem

* <https://chembl.gitbook.io/unichem/webservices>

```
$ python3 -m BioClients.emblebi.unichem.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--src_id_in SRC_ID_IN]
                 [--src_id_out SRC_ID_OUT] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {getFromSourceId,listSources,getFromInchi,getFromInchikey}

EMBL-EBI Unichem client

positional arguments:
  {getFromSourceId,listSources,getFromInchi,getFromInchikey}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             Input IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input IDs (comma-separated)
  --src_id_in SRC_ID_IN
  --src_id_out SRC_ID_OUT
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose
```


Sources on May 3, 2022:

|src\_id|name|name\_label|name\_long|
|---|---|---|---|
|1|chembl|ChEMBL|ChEMBL|
|2|drugbank|DrugBank|DrugBank|
|3|pdb|PDBe|PDBe (Protein Data Bank Europe)|
|4|gtopdb|Guide to Pharmacology|Guide to Pharmacology|
|5|pubchem\_dotf|PubChem: Drugs of the Future|PubChem ('Drugs of the Future' subset)|
|6|kegg\_ligand|KEGG Ligand|KEGG (Kyoto Encyclopedia of Genes and Genomes) Ligand|
|7|chebi|ChEBI|ChEBI (Chemical Entities of Biological Interest).|
|8|nih\_ncc|NIH Clinical Collection|NIH Clinical Collection|
|9|zinc|ZINC|ZINC|
|10|emolecules|eMolecules|eMolecules|
|12|atlas|Atlas|Gene Expression Atlas|
|14|fdasrs|FDA SRS|FDA/USP Substance Registration System (SRS)|
|15|surechembl|SureChEMBL|SureChEMBL|
|16|euos|EU-OPENSCREEN|EU-OPENSCREEN|
|17|pharmgkb|PharmGKB|PharmGKB|
|18|hmdb|Human Metabolome Database|Human Metabolome Database (HMDB)|
|19|wdi|WDI|WDI|
|20|selleck|Selleck|Selleck|
|21|pubchem\_tpharma|PubChem: Thomson Pharma|PubChem ('Thomson Pharma' subset)|
|22|pubchem|PubChem|PubChem Compounds|
|23|mcule|Mcule|Mcule|
|24|nmrshiftdb2|NMRShiftDB|NMRShiftDB|
|25|lincs|LINCS|Library of Integrated Network-based Cellular Signatures|
|26|actor|ACToR|ACToR|
|27|recon|Recon|Recon|
|28|molport|MolPort|MolPort|
|29|nikkaji|Nikkaji|Nikkaji|
|30|ncc|NCC|NCC|
|31|bindingdb|BindingDB|BindingDB|
|32|comptox|EPA CompTox Dashboard|EPA (Environmental Protection Agency) CompTox Dashboard|
|33|lipidmaps|LipidMaps|LipidMaps|
|34|drugcentral|DrugCentral|DrugCentral|
|35|carotenoiddb|CarotenoidDB|Carotenoid Database|
|36|metabolights|Metabolights|Metabolights|
|37|brenda|Brenda|Brenda|
|38|rhea|Rhea|Rhea|
|39|chemicalbook|ChemicalBook|ChemicalBook|
|40|dailymed\_old|DailyMed|DailyMed|
|41|swisslipids|SwissLipids|SwissLipids|
|43|gsrs|GSRS|Global Substance Registration System|
|45|dailymed|DailyMed|DailyMed|
|46|clinicaltrials|clinicaltrials|clinicaltrials|
|47|rxnorm|rxnorm|rxnorm|
|48|MedChemExpress|MedChemExpress|MedChemExpress|
|81|jochem\_id|Jochem\_ID|Jochem\_ID|
|82|jochem\_cas|Jochem\_CAS|Jochem\_CAS|
|83|jochem\_name|Jochem\_Name|Jochem\_Name|
