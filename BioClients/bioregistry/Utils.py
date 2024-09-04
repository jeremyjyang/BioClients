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
    data = {"id":[id_this]}
    data.update({tag:[thing[tag] if tag in thing else None] for tag in tags})
    df_this = pd.DataFrame(data)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out ({etype}): {n_out}")
  return df

#############################################################################
def GetReference(ids, prefix, base_url=API_BASE_URL, fout=None):
  df=None; n_out=0;
  for id_this in ids:
    response = requests.get(f"{base_url}/reference/{prefix}:{id_this}")
    logging.debug(json.dumps(response.json(), indent=2))
    result = response.json()
    providers = result["providers"] if "providers" in result else []
    for provider,url_this in providers.items():
      df_this = pd.DataFrame({"prefix":[prefix], "id":[id_this], "provider_name":[provider], "provider_url":[url_this]})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
