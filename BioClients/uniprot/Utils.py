#!/usr/bin/env python3
##############################################################################
### Utility functions for access to Uniprot REST API.
### UniprotKB = Uniprot Knowledge Base
### https://www.uniprot.org/api-documentation/uniprotkb
##############################################################################
import sys,os,re,json,logging
#
import requests,tqdm
#
API_HOST='rest.uniprot.org'
API_BASE_PATH='/uniprotkb'
#
#############################################################################
def GetData(base_uri, ids, fout):
  n_prot=0; n_err=0;
  params = {
    "fields": [
      "accession",
      "protein_name",
      "cc_function",
      "ft_binding"
    ]
  }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    n_prot+=1
  logging.info(f"n_in: {len(ids)}; n_prot: {n_prot}; n_err: {n_err}")

#############################################################################
