#!/usr/bin/env python3
"""
EMBL-EBI Unichem
New API: https://www.ebi.ac.uk/unichem/api/docs
https://chembl.gitbook.io/unichem/webservices
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/unichem/api/v1'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
HEADERS = {"Accept":"application/json", "Content-Type":"application/json"}
#
##############################################################################
def ListSources(base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  response = requests.get(f"{base_url}/sources")
  logging.debug(response.text)
  result = response.json()
  for source in result['sources']:
    if not tags:
      tags = list(source.keys())
      for tag in tags[:]:
        if type(source[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[source[tag]] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetFromSourceId(ids, src_id_in, src_id_out=None, skip=None, nmax=None, base_url=API_BASE_URL, fout=None):
  n_out=0; df=None;
  compound_tags=None; source_tags=None;
  query = {"sourceID":src_id_in, "type":"sourceID"}
  for i in tqdm.trange(len(ids)):
    if skip is not None and i<skip: continue
    id_this = ids[i]
    query["compound"] = id_this
    try:
      response = requests.post(f"{base_url}/compounds", data=json.dumps(query), headers=HEADERS)
    except Exception as e:
      logging.error(str(e))
      continue
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      continue
    logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    for compound in result["compounds"]:
      logging.debug(json.dumps(compound, indent=2))
      if not compound_tags:
        compound_tags = list(compound.keys())
        for tag in compound_tags[:]:
          if type(compound[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            compound_tags.remove(tag)
      for source in compound["sources"]:
        logging.debug(json.dumps(source, indent=2))
        if not source_tags:
          source_tags = list(source.keys())
          for tag in source_tags[:]:
            if type(source[tag]) in (list, dict):
              logging.info(f"Ignoring field: {tag}")
              source_tags.remove(tag)
        if src_id_out is not None:
          if source["id"] != src_id_out:
            continue
        df_this = pd.DataFrame({'src_id_in':[src_id_in], 'src_compound_id_in':[id_this]})
        df_this = pd.concat([df_this, pd.DataFrame({f"compound_{tag}":[compound[tag]] for tag in compound_tags})], axis=1)
        df_this = pd.concat([df_this, pd.DataFrame({f"source_{tag}":[source[tag]] for tag in source_tags})], axis=1)
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
        n_out += df_this.shape[0]
    if nmax is not None:
      if i>=(nmax if skip is None else nmax+skip): break
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetFromInchi(ids, inchi_rep, search_components=False, src_id_in=None, src_id_out=None, skip=None, nmax=None, base_url=API_BASE_URL, fout=None):
  n_out=0; df=None;
  compound_tags=None; source_tags=None;
  query = {"searchComponents":search_components, "type":inchi_rep}
  if src_id_in is not None: query["sourceID"] = src_id_in
  for i in tqdm.trange(len(ids)):
    if skip is not None and i<skip: continue
    id_this = ids[i]
    query["compound"] = id_this
    response = requests.post(f"{base_url}/connectivity", data=json.dumps(query), headers=HEADERS)
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      continue
    logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    compound = result["searchedCompound"]
    if not compound_tags:
      compound_tags = list(compound.keys())
      for tag in compound_tags[:]:
        if type(compound[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          compound_tags.remove(tag)
    for source in result["sources"]:
      logging.debug(json.dumps(source, indent=2))
      if not source_tags:
        source_tags = list(source.keys())
        for tag in source_tags[:]:
          if type(source[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            source_tags.remove(tag)
      if src_id_out is not None:
        if source["id"] != src_id_out:
          continue
      df_this = pd.DataFrame({f"searchedCompound_{tag}":[compound[tag]] for tag in compound_tags})
      df_this = pd.concat([df_this, pd.DataFrame({f"source_{tag}":[source[tag]] for tag in source_tags})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    if nmax is not None:
      if i>=(nmax if skip is None else nmax+skip): break
  logging.info(f"n_out: {n_out}")
  return df

