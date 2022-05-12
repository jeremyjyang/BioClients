#!/usr/bin/env python3
"""
EMBL-EBI Unichem
https://chembl.gitbook.io/unichem/webservices
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/unichem/rest'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
#
##############################################################################
def GetFromSourceId(ids, src_id_in, src_id_out=None, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/src_compound_id/{id_this}/{src_id_in}/{src_id_out if src_id_out else ''}")
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      continue
    logging.debug(response.text)
    things = response.json()
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({'src_id_in':[src_id_in], 'src_compound_id_in':[id_this]})
      df_this = pd.concat([df_this, pd.DataFrame({tag:[thing[tag]] for tag in tags})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListSources(base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  response = requests.get(f"{base_url}/src_ids")
  logging.debug(response.text)
  things = response.json()
  src_ids = [thing['src_id'] for thing in things]
  for src_id in src_ids:
    response = requests.get(f"{base_url}/sources/{src_id}")
    logging.debug(response.text)
    thing = response.json()[0]
    if not tags:
      tags = list(thing.keys())
      for tag in tags[:]:
        if type(thing[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[thing[tag]] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
