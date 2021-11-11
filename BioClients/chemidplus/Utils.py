#!/usr/bin/env python3
"""
Utility functions for the NLM ChemIDplus REST API.
https://chem.nlm.nih.gov/chemidsearch/api
https://chem.nlm.nih.gov/api/swagger-ui.html
https://chem.nlm.nih.gov/api/v2/api-docs
"""
###
import sys,os,io,re,csv,json,time,logging,tempfile,tqdm
import requests
import urllib.request,urllib.parse
import pandas as pd
#
#
API_HOST='chem.nlm.nih.gov'
API_BASE_PATH='/api'
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
# 
#############################################################################
def ListSources(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  url = (base_url+f"/data/meta/sources")
  response = requests.get(url, headers={"Accept": "application/json"})
  sources = response.json()
  for source in sources:
    if not tags:
      tags = list(source.keys())
    df_this = pd.DataFrame({tag:[source[tag] if tag in source else ""] for tag in tags})
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"Output records: {n_out}")
  return df

#############################################################################
def ListTypes(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  url = (base_url+f"/data/meta/types")
  response = requests.get(url, headers={"Accept": "application/json"})
  types = response.json()
  for type_this in types:
    if not tags:
      tags = list(type_this.keys())
    df_this = pd.DataFrame({tag:[type_this[tag] if tag in type_this else ""] for tag in tags})
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"Output records: {n_out}")
  return df

# /data/rn/auto/50-00-0?data=summary&format=json
#############################################################################
def GetId2Summary(ids, id_type, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    url = (base_url+f"/data/{id_type}/equals/{id_this}?data=summary&format=json")
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="ids")
    response = requests.get(url, headers={"accept": "application/json"})
    logging.debug(response.text)
    if response.status_code==requests.codes.not_found:
      continue
    if response.status_code!=requests.codes.ok:
      logging.error(f"HTTP status_code: {response.status_code}")
    results = response.json()
    n_this = results["total"]
    mols = results["results"]
    for mol in mols:
      chemid = mol["id"] if "id" in mol else None
      lastMod = mol["lastMod"] if "lastMod" in mol else None
      summary = mol["summary"] if "summary" in mol else {}
      if not tags:
        tags = list(summary.keys())
        for tag in tags[:]:
          if type(summary[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field: "{tag}"')
      data_this = {"id": [chemid], "lastMod":[lastMod]}
      for tag in tags:
        data_this[tag] = [summary[tag]] if tag in summary else [""]
      df_this = pd.DataFrame(data_this)
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
    tq.update(n=1)
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df

#############################################################################
def GetId2Names(ids, id_type, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    url = (base_url+f"/data/{id_type}/equals/{id_this}?data=names&format=tsv")
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="ids")
    response = requests.get(url)
    logging.debug(response.text)
    if response.status_code==requests.codes.not_found:
      continue
    if response.status_code!=requests.codes.ok:
      logging.error(f"HTTP status_code: {response.status_code}")
    df_this = pd.read_csv(io.StringIO(response.text), sep='\t')
    df_this = df_this.drop("Last Modified", 1).drop(0, 0) #Drop Last Modified col, row
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
    tq.update(n=1)
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df

#############################################################################
def GetId2ToxicityList(ids, id_type, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    url = (base_url+f"/data/{id_type}/equals/{id_this}?data=toxicityList&format=tsv")
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="ids")
    response = requests.get(url)
    logging.debug(response.text)
    if response.status_code==requests.codes.not_found:
      continue
    if response.status_code!=requests.codes.ok:
      logging.error(f"HTTP status_code: {response.status_code}")
    df_this = pd.read_csv(io.StringIO(response.text), sep='\t')
    df_this = df_this.drop("Last Modified", 1).drop(0, 0) #Drop Last Modified col, row
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
    tq.update(n=1)
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df
