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
def GetCompound2Scaffolds(ids, database, max_rings, base_url=BASE_URL, fout=None):
  tags=[]; n_out=0; df=None;
  headers={'Accept': 'application/json'}
  url = f"{base_url}/compound_search/get_associated_scaffolds"
  params['database'] = database
  params['max_rings'] = max_rings
  for id_this in ids:
    params['SMILES'] = urllib.parse.quote(id_this)
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    scafs = results[id_this]
    for scaf in scafs:
      if not tags:
        tags = [tag for tag in scaf.keys() if type(scaf[tag]) not in (list,dict)]
      df_this = pd.DataFrame({tag:[scaf[tag] if tag in scaf else ""] for tag in tags})
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"IDs: {len(ids)}; Scafs: {n_out}")
  return df

##############################################################################
