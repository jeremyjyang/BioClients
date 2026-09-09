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
  response = requests.get(base_url+f"/data/meta/sources")
  sources = response.json()
  for source in sources:
    if not tags: tags = list(source.keys())
    df_this = pd.DataFrame({tag:[source[tag] if tag in source else ""] for tag in tags})
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"Output records: {n_out}")
  return df

#############################################################################
def ListTypes(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  response = requests.get(base_url+f"/data/meta/types")
  types = response.json()
  for type_this in types:
    if not tags: tags = list(type_this.keys())
    df_this = pd.DataFrame({tag:[type_this[tag] if tag in type_this else ""] for tag in tags})
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"Output records: {n_out}")
  return df

#############################################################################
def GetId2Data(ids, id_type, datatype, base_url=BASE_URL, fout=None):
  n_out=0; n_notfound=0; n_err=0; df=None;
  for i in tqdm.tqdm(range(len(ids))):
    id_this = ids[i]
    url = (base_url+f"/data/{id_type}/equals/{id_this}?data={datatype}&format=tsv")
    response = requests.get(url)
    if response.status_code!=requests.codes.ok:
      logging.info(f"HTTP status_code: {response.status_code}; ID: \"{id_this}\"")
    if response.status_code==requests.codes.not_found:
      n_notfound+=1
      continue
    df_this = pd.read_csv(io.StringIO(response.text), sep='\t')
    if datatype != "summary":
      df_this = df_this.drop("Last Modified", 1).drop(0, 0) #Drop Last Modified col, row
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
  logging.info(f"Input IDs: {len(ids)}; not_found: {n_notfound}; output records: {n_out}")
  return df

#############################################################################
def GetId2Summary(ids, id_type, base_url=BASE_URL, fout=None):
  return GetId2Data(ids, id_type, "summary", base_url, fout)

#############################################################################
def GetId2Names(ids, id_type, base_url=BASE_URL, fout=None):
  return GetId2Data(ids, id_type, "names", base_url, fout)

#############################################################################
def GetId2Numbers(ids, id_type, base_url=BASE_URL, fout=None):
  return GetId2Data(ids, id_type, "numbers", base_url, fout)

#############################################################################
def GetId2ToxicityList(ids, id_type, base_url=BASE_URL, fout=None):
  return GetId2Data(ids, id_type, "toxicityList", base_url, fout)
