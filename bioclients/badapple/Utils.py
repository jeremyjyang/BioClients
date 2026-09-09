#!/usr/bin/env python3
"""
"""
###
import sys,os,io,re,time,requests,urllib,json,logging
import pandas as pd
#
API_HOST='chiltepin.health.unm.edu'
API_BASE_PATH='/badapple2/api/v1'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
DATABASES = ["badapple2", "badapple_classic"]
#
##############################################################################
def GetCompound2Scaffolds(smis, database, max_rings, base_url=BASE_URL, fout=None):
  params = {}; n_out=0; df=None;
  tags = ["id", "in_db", "prank", "pscore", "in_drug", "nass_active", "nass_tested", "ncpd_active", "ncpd_tested", "ncpd_total", "nsam_active", "nsam_tested", "nsub_active", "nsub_tested", "nsub_total", "scafsmi", "kekule_scafsmi", "scaftree" ]
  headers = {'Accept': 'application/json'}
  url = f"{base_url}/compound_search/get_associated_scaffolds_ordered"
  params['database'] = database
  params['max_rings'] = max_rings
  for smi_this in smis:
    vals = re.split(r'\s+', smi_this, 1)
    if len(vals)>1:
      params['SMILES'],params['Names'] = vals
    else:
      params['SMILES'],params['Names'] = smi_this, "Unspecified"
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    scafs = results[0]["scaffolds"]
    for scaf in scafs:
      scaf_this = {"molecule_SMILES": params['SMILES'], "molecule_Name": params['Names'], "db": database}
      for tag in tags:
        scaf_this[tag] = scaf[tag] if tag in scaf else ""
      df_this = pd.DataFrame([scaf_this])
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"Compounds: {len(smis)}; Scaffolds: {n_out}")
  return df

##############################################################################
def GetScaffoldInfo(ids, database, base_url=BASE_URL, fout=None):
  params = {}; n_out=0; df=None;
  tags = ["id", "scafsmi", "kekule_scafsmi", "pscore", "prank", "in_drug", "nass_active", "nass_tested", "ncpd_active", "ncpd_tested", "ncpd_total", "nsam_active", "nsam_tested", "nsub_active", "nsub_tested", "nsub_total", "scaftree"]
  headers = {'Accept': 'application/json'}
  url = f"{base_url}/scaffold_search/get_scaffold_info"
  params['database'] = database
  for id_this in ids:
    params['scafid'] = id_this
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    scaf = results
    scaf_this = {"db": database}
    for tag in tags:
      scaf_this[tag] = scaf[tag] if tag in scaf else ""
    df_this = pd.DataFrame([scaf_this])
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"Scaffolds: {n_out}")
  return df

##############################################################################
def GetScaffold2Compounds(ids, database, base_url=BASE_URL, fout=None):
  params = {}; n_out=0; df=None;
  tags = ["cansmi", "cid", "isosmi", "nass_active", "nass_tested", "nsam_active", "nsam_tested", "nsub_active", "nsub_tested", "nsub_total"]
  headers = {'Accept': 'application/json'}
  url = f"{base_url}/scaffold_search/get_associated_compounds"
  params['database'] = database
  for id_this in ids:
    params['scafid'] = id_this
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    cpds = results
    for cpd in cpds:
      cpd_this = {"scafid": id_this, "db": database}
      for tag in tags:
        cpd_this[tag] = cpd[tag] if tag in cpd else ""
      df_this = pd.DataFrame([cpd_this])
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"Scaffolds: {len(ids)}; Compounds: {n_out}")
  return df

##############################################################################
def GetScaffold2Drugs(ids, database, base_url=BASE_URL, fout=None):
  params = {}; n_out=0; df=None;
  tags = ["cansmi", "cid", "isosmi", "nass_active", "nass_tested", "nsam_active", "nsam_tested", "nsub_active", "nsub_tested", "nsub_total"]
  headers = {'Accept': 'application/json'}
  url = f"{base_url}/scaffold_search/get_associated_drugs"
  params['database'] = database
  for id_this in ids:
    params['scafid'] = id_this
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    cpds = results
    for cpd in cpds:
      cpd_this = {"scafid": id_this, "db": database}
      for tag in tags:
        cpd_this[tag] = cpd[tag] if tag in cpd else ""
      df_this = pd.DataFrame([cpd_this])
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"Scaffolds: {len(ids)}; Drugs: {n_out}")
  return df

##############################################################################
