#!/usr/bin/env python3
"""
Utility functions for ChEBI SOAP API.
https://www.ebi.ac.uk/chebi/webServices.do
"""
###
import sys,os,re,json,time,urllib.parse,logging,tqdm
import pandas as pd
import requests
import collections
import xmltodict
#
NCHUNK=100
#
API_HOST="www.ebi.ac.uk"
API_BASE_PATH="/webservices/chebi/2.0/test"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def GetEntity(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getCompleteEntity?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getCompleteEntityResponse"]["return"]
    except Exception as e:
      continue
    logging.debug(json.dumps(result, indent=2))
    if not tags: tags = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
def GetEntityChildren(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getOntologyChildren?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getOntologyChildrenResponse"]["return"]
    except Exception as e:
      continue
    logging.debug(json.dumps(result, indent=2))
    children = result["ListElement"] if "ListElement" in result else []
    if type(children) is collections.OrderedDict: children = [children]
    for child in children:
      if not tags: tags = [tag for tag in child.keys() if type(child[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[child[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
def GetEntityParents(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getOntologyParents?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getOntologyParentsResponse"]["return"]
    except Exception as e:
      continue
    logging.debug(json.dumps(result, indent=2))
    parents = result["ListElement"] if "ListElement" in result else []
    if type(parents) is collections.OrderedDict: parents = [parents]
    for parent in parents:
      if not tags: tags = [tag for tag in parent.keys() if type(parent[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[parent[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
