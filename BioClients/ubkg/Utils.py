#!/usr/bin/env python3
"""
Utility functions for UBKG REST API.
See: https://smart-api.info/ui/96e5b5c0b0efeef5b93ea98ac2794837 (includes DDKG context)
C0006142,C0678222
"""
import sys,os,re,requests,urllib,json,time,logging,tqdm
import pandas as pd

#
#API_HOST="datadistillery.api.sennetconsortium.org"
API_HOST="ubkg.api.xconsortia.org"
API_BASE_PATH=""
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
CONTEXTS = ["base_context", "data_distillery_context", "hubmap_sennet_context"]
#
HEADERS={"Accept":"application/json"}
#
##############################################################################
def Info(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/database/server", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame({"field":result.keys(), "value":result.values()})
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
def ListSABs(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/sabs", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame({"sabs":result["sabs"]})
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
def ListSources(context, sab, api_key, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags=None;
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+f"/sources?context={context}", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  sources = result["sources"]
  for source in sources:
    if not tags:
      tags = list(source.keys())
    for tag in tags:
      if type(source[tag]) in (dict, list, tuple):
        if len(source[tag])>0:
          if tag=="citations":
            source[tag] = ";".join([v["url"] for v in source[tag]])
          elif tag=="contexts":
            source[tag] = ";".join(source[tag])
          elif tag=="home_urls":
            source[tag] = ";".join(source[tag])
          elif tag=="licenses":
            source[tag] = ";".join(["{}:{}:{}".format(v["type"], v["subtype"], v["version"]) for v in source[tag]])
          else:
            source[tag] = ";".join([str(v) for v in source[tag]])
        else:
          source[tag] = str(source[tag])
      df_this = pd.DataFrame({tag:[(source[tag] if tag in source else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
  logging.info(f"Sources: {n_out}")
  return df

##############################################################################
def ListNodeTypes(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/node-types", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame(result)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Node-types: {df.shape[0]}")
  return df

##############################################################################
def ListNodeTypeCounts(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  node_types = ListNodeTypes(api_key, base_url)["node_types"]
  n_type=0; n_out=0; df=None;
  for node_type in node_types:
    n_type+=1
    response = requests.get(f"{base_url}/node-types/{node_type}/counts", headers=headers)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    df_this = pd.DataFrame(result)
    df_this.insert(loc=0, column='node_type', value=node_type)
    df_this = df_this[["node_type", "total_count"]]
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
  return df

##############################################################################
def ListRelationshipTypes(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/relationship-types", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame(result)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Relationship-types: {df.shape[0]}")
  return df

##############################################################################
def ListPropertyTypes(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/property-types", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame(result)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Property-types: {df.shape[0]}")
  return df

##############################################################################
def ListSemanticTypes(api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get(base_url+"/semantics/semantic-types", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  semantic_types = result["semantic_types"]
  df = pd.DataFrame.from_records(semantic_types)
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Semantic-types: {df_this.shape[0]}")
  return df

##############################################################################
def GetConcept2Codes(ids, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  n_in=0; n_out=0; n_code=0; df=None;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/codes", headers=headers)
    if not response:
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    codes = result
    if not codes or len(codes)==0: continue
    df_this = pd.DataFrame({"concept":[id_this for i in range(len(codes))], "code":codes})
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
    n_code += len(codes)
  logging.info(f"Concepts in: {n_in}; out: {n_out}; codes out: {n_code}")
  return df

##############################################################################
def GetConcept2Concepts(ids, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  n_in=0; n_out=0; n_concept=0; df=None;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/concepts", headers=headers)
    if not response:
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    concepts = result
    if not concepts or len(concepts)==0: continue
    df_this = pd.DataFrame.from_records(concepts)
    df_this.columns = ["conceptB", "preftermB", "relationship", "sabB"]
    df_this.insert(loc=0, column='conceptA', value=id_this)
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
    n_concept += len(concepts)
  logging.info(f"Concepts in: {n_in}; out: {n_out}; concepts out: {n_concept}")
  return df

##############################################################################
def GetConcept2Definitions(ids, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  n_in=0; n_out=0; n_def=0; df=None;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/definitions", headers=headers)
    if not response:
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    defs = result
    if not defs or len(defs)==0: continue
    df_this = pd.DataFrame.from_records(defs)
    df_this = df_this[["sab", "definition"]]
    df_this.insert(loc=0, column='concept', value=id_this)
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += 1
    n_def += len(defs)
  logging.info(f"Concepts in: {n_in}; out: {n_out}; defs out: {n_def}")
  return df

##############################################################################
def GetConcept2Paths(ids, sab, rel, mindepth, maxdepth, api_key, base_url=BASE_URL, fout=None):
  '''JSON output'''
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  n_in=0; n_node_out=0; n_edge_out=0;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/paths/expand?sab={sab}&rel={rel}&mindepth={mindepth}&maxdepth={maxdepth}&skip=0&limit=10", headers=headers)
    if not response:
      continue
    result = response.json()
    n_edge_out += len(result["edges"])
    n_node_out += len(result["nodes"])
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if fout: fout.write(json.dumps(result, sort_keys=True, indent=2))
  logging.info(f"Concepts in: {n_in}; nodes out: {n_node_out}; edges out: {n_edge_out}")

##############################################################################
def GetConcept2Trees(ids, sab, rel, mindepth, maxdepth, api_key, base_url=BASE_URL, fout=None):
  '''JSON output'''
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  n_in=0; n_node_out=0; n_edge_out=0;
  for id_this in ids:
    n_in += 1
    response = requests.get(f"{base_url}/concepts/{id_this}/paths/trees?sab={sab}&rel={rel}&mindepth={mindepth}&maxdepth={maxdepth}&skip=0&limit=10", headers=headers)
    if not response:
      continue
    result = response.json()
    n_edge_out += len(result["edges"])
    n_node_out += len(result["nodes"])
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if fout: fout.write(json.dumps(result, sort_keys=True, indent=2))
  logging.info(f"Concepts in: {n_in}; nodes out: {n_node_out}; edges out: {n_edge_out}")

##############################################################################
def GetTerm2Concepts(term, api_key, base_url=BASE_URL, fout=None):
  headers = {**HEADERS, **{"UMLS-Key": api_key}}
  response = requests.get("{}/terms/{}/concepts".format(base_url, urllib.parse.quote(term)), headers=headers)
  if not response:
    logging.info(f"Not found: {term}")
    return
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  concepts = result
  if not concepts or len(concepts)==0:
    logging.info(f"Not found: {term}")
    return
  df = pd.DataFrame({"term":[term for i in range(len(concepts))], "concept":concepts})
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Concepts out: {df.shape[0]}")
  return df

