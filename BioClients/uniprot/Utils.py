#!/usr/bin/env python3
##############################################################################
### Utility functions for access to Uniprot REST API.
### UniprotKB = Uniprot Knowledge Base
### https://www.uniprot.org/api-documentation/uniprotkb
##############################################################################
import sys,os,re,json,logging
#
import requests,tqdm
import pandas as pd
#
API_HOST='rest.uniprot.org'
API_BASE_PATH='/uniprotkb'
#
#############################################################################
def GetNames(base_uri, ids, fout):
  n_out=0; n_err=0;
  tags_pro = ["entryType", "primaryAccession"]
  params = { "fields": [ "accession", "protein_name" ] }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    df_this_base = pd.DataFrame({tag:([str(result[tag])] if tag in result else ['']) for tag in tags_pro})

    proDes = result['proteinDescription'] if 'proteinDescription' in result else {}

    flag = proDes['flag'] if 'flag' in proDes else None
    df_this_0 = pd.DataFrame({ 'queryId':[id_this], 'flag':[flag] })

    recNam = proDes['recommendedName'] if 'recommendedName' in proDes else {}
    fullNam = recNam['fullName']['value'] if 'fullName' in recNam and 'value' in recNam['fullName'] else None
    shortNams = recNam['shortNames'] if 'shortNames' in recNam else []
    shortNams_str = ";".join([sN['value'] for sN in shortNams])
    altNams = proDes['alternativeNames'] if 'alternativeNames' in proDes else []
    altNams_str = ";".join([(aN['fullName']['value'] if 'fullName' in aN and 'value' in aN['fullName'] else '') for aN in altNams])
    df_this_names = pd.DataFrame({
        'fullName':[fullNam],
        'shortNames':[shortNams_str],
        'altNames':[altNams_str]
        })
    df_this = pd.concat([df_this_0, df_this_base, df_this_names], axis=1)
    if fout is not None:
      df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += 1
    if fout is None: df = pd.concat([df, df_this])

  logging.info(f"n_in: {len(ids)}; n_out: {n_out}; n_err: {n_err}")

#############################################################################
def GetFunctions(base_uri, ids, fout):
  n_out=0; n_err=0;
  tags_pro = ["entryType", "primaryAccession"]
  params = { "fields": [ "accession", "cc_function" ] }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    comments = result['comments'] if 'comments' in result else []
    cType = comments['commentType'] if 'commentType' in comments else None
    texts = comments['texts'] if 'texts' in comments else []


    df_this_base = pd.DataFrame({tag:([str(result[tag])] if tag in result else ['']) for tag in tags_pro})



#############################################################################
def GetData(base_uri, ids, fout):
  n_prot=0; n_err=0;
  params = {
    "fields": [
      "accession",
      "protein_name",
      "cc_function",
      "ft_binding"
    ]
  }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    n_prot+=1
  logging.info(f"n_in: {len(ids)}; n_prot: {n_prot}; n_err: {n_err}")

#############################################################################
