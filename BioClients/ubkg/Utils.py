#!/usr/bin/env python3
"""
Utility functions for UBKG REST API.
See: https://smart-api.info/ui/55be2831c69b17f6bc975ddb58cabb5e
"""
import sys,os,re,requests,urllib,json,time,logging,tqdm
import pandas as pd

#
API_HOST="datadistillery.api.sennetconsortium.org"
API_BASE_PATH=""
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
HEADERS={"Accept":"application/json"}
#
##############################################################################
def Info(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"X-API-KEY": api_key}}
  response = requests.get(base_url+"/database/server", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame({"field":result.keys(), "value":result.values()})
  if fout: df.to_csv(fout, "\t", index=False)
  return df

##############################################################################
def GetConcept2Codes(ids, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"X-API-KEY": api_key}}
  n_in=0; n_out=0; n_code=0; df=None;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/codes", headers=headers)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    codes = result
    if not codes or len(codes)==0: continue
    df_this = pd.DataFrame({"cui":[id_this for i in range(len(codes))], "code":codes})
    if fout: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
    n_code += len(codes)
  logging.info(f"Concepts in: {n_in}; out: {n_out}; codes out: {n_code}")
  return df

##############################################################################
def GetConcept2Concepts(ids, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"X-API-KEY": api_key}}
  n_in=0; n_out=0; n_concept=0; df=None;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/concepts", headers=headers)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    concepts = result
    if not concepts or len(concepts)==0: continue
    df_this = pd.DataFrame({"cui_A":[id_this for i in range(len(concepts))], "cui_B":concepts})
    if fout: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
    n_concept += len(concepts)
  logging.info(f"Concepts in: {n_in}; out: {n_out}; concepts out: {n_concept}")
  return df

##############################################################################
##############################################################################
