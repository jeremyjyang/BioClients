#!/usr/bin/env python3
"""
Utility functions for Oncotree REST API.
See: https://oncotree.mskcc.org/
See: https://oncotree.mskcc.org/#/home
"""
import sys,os,re,requests,urllib,json,time,logging,tqdm
import pandas as pd

#
API_HOST="oncotree.mskcc.org"
API_BASE_PATH="/api"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
HEADERS={"Accept":"application/json"}
#
##############################################################################
def Info(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+"/info", headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))

##############################################################################
def ListVersions(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+'/versions', headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  versions = result
  df = pd.DataFrame.from_records(versions)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Versions: {len(versions)}")
  return df

##############################################################################
def ListMainTypes(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+'/mainTypes', headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  maintypes = result
  maintypes.sort()
  df = pd.DataFrame({"main_types": maintypes})
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Main types: {len(maintypes)}")
  return df

##############################################################################
def ListTumorTypes(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+'/tumorTypes', headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  tumortypes = result
  df = pd.DataFrame.from_records(tumortypes)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Tumor types: {len(tumortypes)}")
  return df

##############################################################################
def SearchTumorTypes(qry, qtype, exact, levels, base_url=BASE_URL, fout=None):
  response = requests.get(base_url+f"/tumorTypes/search/{qtype}/{qry}?exactMatch={str(exact)}&levels={urllib.parse.quote(levels)}", headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  tumortypes = result
  df = pd.DataFrame.from_records(tumortypes)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Tumor types: {len(tumortypes)}")
  return df

##############################################################################
