#!/usr/bin/env python3
"""
Utility functions for GlyCan REST API.
https://api.glygen.org/

curl -X GET "https://api.glygen.org/glycan/detail/G00053MO/" -H "accept: application/json"
"""
###
import sys,os,re,json,collections,time,urllib.parse,logging,tqdm,tqdm.auto
import pandas as pd
import requests
#
NCHUNK=100
#
API_HOST="api.glygen.org"
API_BASE_PATH=""
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def GetGlycans(ids, skip, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for i in tqdm.auto.trange(len(ids), desc="IDs"):
    id_this = ids[i]
    response = requests.get(f"{base_url}/glycan/detail/{id_this}", headers={"Content-Type":"application/json"})
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    if not tags: tags = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListGlycans(skip, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; tq=None;
  while True:
    url = f"""{base_url}/directsearch/glycan/?query={{"offset":{skip+1},"limit":{NCHUNK}}}"""
    response = requests.get(url, headers={"Content-Type":"application/json"})
    if response is None: break
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      break
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    if len(results["results"])==0: break
    for result in results["results"]:
      if not tags:
        tags = list(result.keys())
        for tag in tags[:]:
          if type(result[tag]) in (list, dict, collections.OrderedDict):
            tags.remove(tag)
            logging.info(f"Ignoring tag: {tag}")
      if tq is None and "queryinfo" in results and "batch" in results["queryinfo"] and "total_hits" in results["queryinfo"]["batch"]:
        total_hits = results["queryinfo"]["batch"]["total_hits"]
        tq = tqdm.tqdm(total=(total_hits-skip))
      df_this = pd.DataFrame({tag:[result[tag] if tag in result else ""] for tag in tags})
      inchi_key = result["inchi_key"]["key"] if "inchi_key" in result and "key" in result["inchi_key"] else ""
      pubchem_cid=""; pubchem_sid=""; chebi_id=""; glytoucan_id="";
      if "crossref" in result:
        for crossref in result["crossref"]:
          if crossref["database"]=="ChEBI": chebi_id = crossref["id"]
          elif crossref["database"]=="PubChem Compound": pubchem_cid = crossref["id"]
          elif crossref["database"]=="PubChem Substance": pubchem_sid = crossref["id"]
          elif crossref["database"]=="GlyTouCan": glytoucan_id = crossref["id"]
      df_this = pd.concat([df_this,
	pd.DataFrame({"inchi_key":[inchi_key], "glytoucan_id":[glytoucan_id], "pubchem_cid":[pubchem_cid], "pubchem_sid":[pubchem_sid], "chebi_id":[chebi_id]})
	], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
      tq.update(n=df_this.shape[0])
    skip += NCHUNK
  tq.close()
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
