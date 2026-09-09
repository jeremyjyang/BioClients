#!/usr/bin/env python3
"""
Utility functions for the CAS REST API.
"""
###
import sys,os,io,re,csv,json,time,logging,tempfile,tqdm
import requests
import urllib.request,urllib.parse
import pandas as pd
#
#
API_HOST='commonchemistry.cas.org'
API_BASE_PATH='/api'
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
# https://commonchemistry.cas.org/api/detail?uri=substance%2Fpt%2F50000
#############################################################################
def GetRN2Details(ids, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    uri = urllib.parse.quote(f"substance/pt/{id_this}")
    url = (base_url+f"/detail?uri={uri}")
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="mols")
    tq.update(n=1)
    response = requests.get(url, headers={"Accept": "application/json"})
    logging.debug(response.text)
    if response.status_code==requests.codes.not_found:
      continue
    if response.status_code!=requests.codes.ok:
      logging.error(f"HTTP status_code: {response.status_code}")
    mol = response.json()
    if not tags:
      tags = list(mol.keys())
      for tag in tags[:]:
        if type(mol[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug(f'Ignoring field: "{tag}"')
      if "image" in tags:
        tags.remove("image")
        logging.debug(f'Ignoring field: "image"')
    synonyms = mol["synonyms"] if "synonyms" in mol else []
    replacedRns = mol["replacedRns"] if "replacedRns" in mol else []
    data_this = {tag:[mol[tag]] for tag in tags}
    data_this["synonyms"] = ",".join(synonyms)
    data_this["replacedRns"] = ",".join(replacedRns)
    df_this = pd.DataFrame(data_this)
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    n_out+=1
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df
