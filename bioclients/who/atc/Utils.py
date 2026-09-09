#!/usr/bin/env python3
"""
https://api.atcddd.fhi.no/swagger/
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='api.atcddd.fhi.no'
API_BASE_PATH='/api/v1/atc'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100
#
##############################################################################
def ListAlterations(year, api_key, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; tags_term=None; df=None;
  size=NCHUNK; skip=0;
  headers = {"Authorization":f"Bearer {api_key}", "Content-Type":"application/json"}
  url_this = f"{base_url}/alterationsForYear?year={year}"
  response = requests.get(url_this, headers=headers)
  #logging.debug(response.text)
  if response.status_code!=200:
    logging.error(f"status_code: {response.status_code} \"{response.text}\"")
    return None
  results = response.json()
  logging.debug(json.dumps(results, sort_keys=True, indent=2)+'\n')
  things = results['alterations']
  if not things:
    return None
  for thing in things:
    if not tags:
      tags = list(thing.keys())
      for tag in tags[:]:
        if type(thing[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
