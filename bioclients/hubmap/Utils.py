#!/usr/bin/env python3
"""
Utility functions for HuBMAP REST API.
https://portal.hubmapconsortium.org/apis
"""
###
import sys,os,re,time,json,logging,requests,tqdm
import pandas as pd
#
API_HOST='entity.api.hubmapconsortium.org'
API_BASE_PATH=''
API_BASE_URL = f"https://{API_HOST}{API_BASE_PATH}"
#
#############################################################################
def ListEntityTypes(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/entity-types")
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  results = response.json()
  if fout is not None:
    for result in results:
      fout.write(f"{result}\n")
  logging.info(f"Entities: {len(results)}")
  return results

#############################################################################
def GetEntity(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; df=None; tq=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/entities/{id_this}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    if fout is not None:
      for result in results:
        fout.write(f"{result}\n")
    n_out += len(results)
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
