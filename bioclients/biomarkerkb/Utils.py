#!/usr/bin/env python3
"""
Utility functions for BiomarkerKB REST API.
https://api.biomarkerkb.org/

"""
###
import sys,os,re,json,collections,time,urllib.parse,logging,tqdm,tqdm.auto
import pandas as pd
import requests
#
NCHUNK=100
#
API_HOST="api.biomarkerkb.org"
API_BASE_PATH=""
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def GetBiomarkerDetail(ids, skip, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for i in tqdm.auto.trange(len(ids), desc="IDs"):
    id_this = ids[i]
    response = requests.get(f"{base_url}/biomarker/detail/{id_this}", headers={"Accept":"application/json"})
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    if not tags: tags = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
