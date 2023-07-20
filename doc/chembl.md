# `BioClients.chembl`

## ChEMBL

Tools for obtaining and processing ChEMBL data.

* <https://www.ebi.ac.uk/chembl/>
* <https://chembl.gitbook.io/chembl-interface-documentation/web-services>
* <https://chembl.gitbook.io/chembl-interface-documentation/downloads>

```
$ python3 -m BioClients.chembl.Client get_drug_indications -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE] [--skip SKIP] [--nmax NMAX]
                 [--dev_phase {0,1,2,3,4}] [--assay_source ASSAY_SOURCE]
                 [--assay_type ASSAY_TYPE] [--pmin PMIN] [--include_phenotypic]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {status,list_sources,list_targets,list_assays,list_docs,list_mols,list_drugs,list_drug_indications,list_tissues,list_cells,list_mechanisms,list_organisms,list_protein_classes,search_assays,search_mols_by_name,get_mol,get_mol_by_inchikey,get_target,get_target_components,get_target_by_uniprot,get_assay,get_activity_by_mol,get_activity_by_assay,get_activity_by_target,get_activity_properties,get_drug_indications,get_document}

ChEMBL REST API client

positional arguments:
  {status,list_sources,list_targets,list_assays,list_docs,list_mols,list_drugs,list_drug_indications,list_tissues,list_cells,list_mechanisms,list_organisms,list_protein_classes,search_assays,search_mols_by_name,get_mol,get_mol_by_inchikey,get_target,get_target_components,get_target_by_uniprot,get_assay,get_activity_by_mol,get_activity_by_assay,get_activity_by_target,get_activity_properties,get_drug_indications,get_document}
                        OPERATION (select one)

options:
  -h, --help            show this help message and exit
  --ids IDS             input IDs (e.g. mol, assay, target, document)
  --i IFILE             input file, IDs
  --o OFILE             output (TSV)
  --skip SKIP
  --nmax NMAX
  --dev_phase {0,1,2,3,4}
                        molecule development phase
  --assay_source ASSAY_SOURCE
                        source_id
  --assay_type ASSAY_TYPE
                        {'B': 'Binding', 'F': 'Functional', 'A': 'ADMET', 'T':
                        'Toxicity', 'P': 'Physicochemical', 'U': 'Unclassified'}
  --pmin PMIN           min pChEMBL activity value (9 ~ 1nM *C50)
  --include_phenotypic  else pChembl required
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Assay types: {'B': 'Binding', 'F': 'Functional', 'A': 'ADMET', 'T': 'Toxicity', 'P':
'Physicochemical', 'U': 'Unclassified'}. Example IDs: CHEMBL2 (compound); CHEMBL1642
(compound & drug); CHEMBL240 (target); CHEMBL1824 (target); CHEMBL1217643 (assay);
CHEMBL3215220 (assay, PubChem assay 519, NMMLSC FPR); Q12809 (Uniprot)
```
