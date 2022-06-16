#!/usr/bin/env python3
"""
Utility functions for BioGRID REST API.
See: http://wiki.thebiogrid.org/doku.php/biogridrest
"""
###
import sys,os,re,json,time,logging,requests,tqdm
import pandas as pd
#
API_HOST="webservice.thebiogrid.org"
API_BASE_PATH=""
API_BASE_URL=f"https://{API_HOST}{API_BASE_PATH}"
#
##############################################################################
def ListOrganisms(params, base_url=API_BASE_URL, fout=None):
  url = f"{base_url}/organisms/?accesskey={params['API_KEY']}&format=json"
  response = requests.get(url)
  organisms = response.json()
  logging.debug(json.dumps(organisms, indent=2))
  df = pd.DataFrame.from_dict(organisms, orient="index")
  df.reset_index(drop=False, inplace=True)
  df.columns = ["organism_id", "organism"]
  if fout is not None: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def ListIdTypes(params, base_url=API_BASE_URL, fout=None):
  url = f"{base_url}/identifiers/?accesskey={params['API_KEY']}&format=json"
  response = requests.get(url)
  idtypes = response.json()
  logging.debug(json.dumps(idtypes, indent=2))
  df = pd.DataFrame.from_dict(idtypes, orient="index")
  df.reset_index(drop=False, inplace=True)
  if fout is not None: df.to_csv(fout, "\t", index=False, header=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def GetInteractions(params, ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url = f"{base_url}/interactions/{id_this}?accesskey={params['API_KEY']}&format=json"
    response = requests.get(url)
    result = response.json()
    logging.debug(json.dumps(result, indent=2, sort_keys=False)+'\n')
    intr = result[id_this]
    if not tags:
      tags = list(intr.keys())
      for tag in tags[:]:
        if type(intr[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[intr[tag]] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def SearchInteractions(params, ids, search_params, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  skip=0; chunk=1000;
  url = f"{base_url}/interactions/{id_this}?accesskey={params['API_KEY']}&format=json"
  if ids:
    url+=f"&geneList={'|'.join(ids)}"
  url+=f"&interSpeciesExcluded={str(not search_params['inc_interspecies']).lower()}"
  url+=f"&selfInteractionsExcluded={str(not search_params['inc_self']).lower()}"
  if search_params['elist']:
    url+=f"&includeEvidence={str(search_params['inc_evidence']).lower()}"
    url+=f"&evidenceList={'|'.join(search_params['elist'])}"
  if search_params['addl_idtypes']:
    url+=f"&additionalIdentifierTypes={'|'.join(search_params['addl_idtypes'])}"
  if search_params['human']:
    url+=f"&taxId=9606"
  while True:
    url_this = url+f"&start={skip}&max={chunk}"
    response = requests.get(url_this)
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      break
    result = response.json()
    logging.debug(json.dumps(result, indent=2, sort_keys=False)+'\n')
    intrs = result
    for id_this, intr in intrs.items():
      if not tags:
        tags = list(intr.keys())
        for tag in tags[:]:
          if type(intr[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[intr[tag]] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    skip+=chunk
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
