#!/usr/bin/env python3
"""
Utility functions for ChEBI REST API.
https://www.ebi.ac.uk/chebi/backend/api/docs/
"""
###
import sys,os,re,json,time,urllib.parse,logging,requests,collections
import pandas as pd
#
API_HOST="www.ebi.ac.uk"
API_BASE_PATH="/chebi/backend/api/public"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
NCHUNK=100
#
##############################################################################
def ListSources(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  response = requests.get(f"{base_url}/advanced_search/sources_list", headers={"Accept":"application/json"})
  result = response.json()
  logging.debug(json.dumps(result, indent=2))
  for source in result:
    if not tags:
      tags = [tag for tag in source.keys() if type(source[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tag:[source[tag] if tag in source else ''] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetEntity(ids, include_parents=False, include_children=False, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url_this = f"{base_url}/compound/{id_this}"
    url_this = f"{url_this}/?{'true' if include_parents else 'false'}&{'true' if include_children else 'false'}"
    response = requests.get(url_this, headers={"Accept":"application/json"})
    result = response.json()
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    if not tags:
      tags = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tag:[result[tag] if tag in result else ''] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetEntityNames(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags_entity=None; tags_name = ["name", "status", "type", "source", "ascii_name", "adapted", "language_code"]
  for id_this in ids:
    url_this = f"{base_url}/compound/{id_this}"
    response = requests.get(url_this, headers={"Accept":"application/json"})
    result = response.json()
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    if not tags_entity:
      tags_entity = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this_entity = pd.DataFrame({tag:[result[tag] if tag in result else ''] for tag in tags_entity})

    names = result["names"] if "names" in result else {}
    synonyms = names["SYNONYM"] if "SYNONYM" in names else []
    iupac_names = names["IUPAC NAME"] if "IUPAC NAME" in names else []
    uniprot_names = names["UNIPROT NAME"] if "UNIPROT NAME" in names else []
    for name in synonyms+iupac_names+uniprot_names:

      df_this_name = pd.DataFrame({tag:[name[tag] if tag in name else ''] for tag in tags_name})
      df_this = pd.concat([df_this_entity, df_this_name], axis=1)
    
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]

  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetEntityDatabaseAccessions(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags_entity=None; tags_dbacc = ["id", "accession_number", "type", "source_name", "url", "prefix"]
  for id_this in ids:
    url_this = f"{base_url}/compound/{id_this}"
    response = requests.get(url_this, headers={"Accept":"application/json"})
    result = response.json()
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    if not tags_entity:
      tags_entity = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this_entity = pd.DataFrame({tag:[result[tag] if tag in result else ''] for tag in tags_entity})

    database_accessions = result["database_accessions"] if "database_accessions" in result else {}
    xrefs = database_accessions["MANUAL_X_REF"] if "MANUAL_X_REF" in database_accessions else []
    cas_rns = database_accessions["CAS"] if "CAS" in database_accessions else []
    rns = database_accessions["REGISTRY_NUMBER"] if "REGISTRY_NUMBER" in database_accessions else []
    citations = database_accessions["CITATION"] if "CITATION" in database_accessions else []

    for acc in xrefs+cas_rns+rns+citations:
      df_this_acc = pd.DataFrame({tag:[acc[tag] if tag in acc else ''] for tag in tags_dbacc})
      if "id" in df_this_acc:
        df_this_acc["accession_id"] = df_this_acc.pop("id")
        df_this_acc = df_this_acc [['accession_id'] + [col for col in df_this_acc.columns if col != 'accession_id']]
    
      df_this = pd.concat([df_this_entity, df_this_acc], axis=1)
    
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]

  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetCompoundData(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags_entity=None; tags_chemical = ["formula", "charge", "mass", "monoisotopic_mass"]
  tags_structure = ["id", "smiles", "standard_inchi", "standard_inchi_key", "wurcs", "is_r_group"]
  for id_this in ids:
    url_this = f"{base_url}/compound/{id_this}"
    response = requests.get(url_this, headers={"Accept":"application/json"})
    result = response.json()
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    if not tags_entity:
      tags_entity = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this_entity = pd.DataFrame({tag:[result[tag] if tag in result else ''] for tag in tags_entity})

    chemical_data = result["chemical_data"] if "chemical_data" in result else {}
    default_structure = result["default_structure"] if "default_structure" in result else {}

    df_this_chemical = pd.DataFrame({tag:[chemical_data[tag] if tag in chemical_data else ''] for tag in tags_chemical})
    df_this_structure = pd.DataFrame({tag:[default_structure[tag] if tag in default_structure else ''] for tag in tags_structure})
    if "id" in df_this_structure:
      df_this_structure["structure_id"] = df_this_structure.pop("id")
      df_this_structure = df_this_structure [['structure_id'] + [col for col in df_this_structure.columns if col != 'structure_id']]
    df_this = pd.concat([df_this_entity, df_this_chemical, df_this_structure], axis=1)

    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]

  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def Search(query, base_url=BASE_URL, fout=None):
  n_out=0; df=None;
  tags_source=[ "chebi_accession", "name", "ascii_name", "stars", "default_structure", "definition", "monoisotopicmass", "charge", "formula", "smiles", "mass", "structures", ];
  url = f"{base_url}/es_search/?term={query}&size={NCHUNK}"
  i_page=1;
  while True:
    url_this = f"{url}&page={i_page}"
    response = requests.get(url_this, headers={"Accept":"application/json"})
    rval = response.json()
    logging.debug(json.dumps(rval, indent=2))
    results = rval["results"] 
    n_total = rval["total"] if "total" in rval else 0
    n_pages = rval["number_pages"] if "number_pages" in rval else 0
    for result in results:
      source_data = result["_source"] if "_source" in result else {}
      df_this = pd.DataFrame({tag:[source_data[tag] if tag in source_data else ''] for tag in tags_source})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    if n_out >= n_total: break
    i_page+=1
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
