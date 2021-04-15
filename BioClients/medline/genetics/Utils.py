#!/usr/bin/env python3
##############################################################################
### Medline Plus Genetics
### https://medlineplus.gov/about/developers/geneticsdatafilesapi/
### https://medlineplus.gov/download/ghr-summaries.xml
##############################################################################
### https://wsearch.nlm.nih.gov/ws/query?db=ghr&term=alzheimer
### https://medlineplus.gov/download/genetics/condition/alzheimer-disease.json
##############################################################################
import sys,os,re,json,argparse,time,logging,requests,urllib.parse
import pandas as pd
import xmltodict
#
#
API_HOST="wsearch.nlm.nih.gov"
API_BASE_PATH="/ws"
#
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def SearchDisease(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  for id_this in ids:
    response = requests.get(f"{base_url}/query?db=ghr&term={urllib.parse.quote(id_this)}")
    #logging.debug(f"response.content: {response.content}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    results = rval_dict["search_results"]["result"]
    for result in results:
      #logging.debug(f"result: {result}")
      if not tags: tags = list(result.keys())
      df_this = pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False)
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

