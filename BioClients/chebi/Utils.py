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
