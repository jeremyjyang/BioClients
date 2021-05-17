#!/usr/bin/env python3
"""
Utility functions for GlyCan REST API.
https://api.glygen.org/

curl -X GET "https://api.glygen.org/glycan/detail/G00053MO/" -H "accept: application/json"
"""
###
import sys,os,re,json,collections,time,urllib.parse,logging,tqdm
import pandas as pd
import requests
#
NCHUNK=100
#
API_HOST="api.glygen.org"
API_BASE_PATH="/glycan"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def Get(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/detail/{id_this}", headers={"Content-Type":"application/json"}).json()
    logging.debug(json.dumps(response, indent=2))
    entity = response
    if not tags: tags = [tag for tag in entity.keys() if type(entity[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tags[j]:[entity[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]

  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
