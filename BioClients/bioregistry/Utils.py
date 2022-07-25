#!/usr/bin/env python3
"""
Bioregistry.io
"""
import sys,os,re,time,json,requests,logging
import pandas as pd
#
API_HOST='bioregistry.io'
API_BASE_PATH='/api'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def ListEntities(etype, base_url=API_BASE_URL, fout=None):
  "Entities: contributors|contexts|collections|registry|metaregistry"
  tags=None; df=None; n_out=0;
  response = requests.get(f"{base_url}/{etype}")
  logging.debug(json.dumps(response.json(), indent=2))
  results = response.json()
  for id_this,thing in results.items():
    if not tags:
      tags = list(thing.keys())
      for tag in tags[:]:
        if type(thing[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else None] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out ({etype}): {n_out}")
  return df

#############################################################################
