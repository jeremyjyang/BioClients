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
import collections
import pandas as pd
import xmltodict
#
#
API_HOST="wsearch.nlm.nih.gov"
DOWNLOAD_HOST="medlineplus.gov"
API_BASE_PATH="/ws"
DOWNLOAD_BASE_PATH="/download"
#
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
DOWNLOAD_BASE_URL='https://'+DOWNLOAD_HOST+DOWNLOAD_BASE_PATH
#
SUMMARY_URL="https://medlineplus.gov/download/ghr-summaries.xml"
#
##############################################################################
def Search(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  for id_this in ids:
    response = requests.get(f"{base_url}/query?db=ghr&term={urllib.parse.quote(id_this)}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    search_results = rval_dict["search_results"]
    count = search_results["@count"]
    query = search_results["query"]
    logging.debug(f"query: {query}; count: {count}")
    results = search_results["result"] if "result" in search_results else []
    for result in results:
      if not tags: tags = list(result.keys())
      df_this = pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
def ListConditions(summary_url=SUMMARY_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  response = requests.get(summary_url)
  logging.debug(f"HTTP Status code: [{response.status_code}]")
  rval_dict = xmltodict.parse(response.content)
  logging.debug(json.dumps(rval_dict, indent=2))
  summaries = rval_dict["summaries"]["health-condition-summary"]
  for summary in summaries:
      if not tags: tags = [tag for tag in summary.keys() if type(summary[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[summary[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
def ListGenes(summary_url=SUMMARY_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  response = requests.get(summary_url)
  logging.debug(f"HTTP Status code: [{response.status_code}]")
  rval_dict = xmltodict.parse(response.content)
  logging.debug(json.dumps(rval_dict, indent=2))
  summaries = rval_dict["summaries"]["gene-summary"]
  for summary in summaries:
      if not tags: tags = [tag for tag in summary.keys() if type(summary[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[summary[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
def GetConditionGenes(ids, base_url=DOWNLOAD_BASE_URL, fout=None):
  """IDs must be terms as in condition URLs, e.g. "alzheimer-disease", from
https://medlineplus.gov/download/genetics/condition/alzheimer-disease.json
  """
  n_out=0; tags=None; df=pd.DataFrame();
  for id_this in ids:
    response = requests.get(f"{base_url}/genetics/condition/{id_this}.json")
    if response.status_code != 200:
      logging.error(f"Condition ID not found [{response.status_code}]: '{id_this}'")
      continue
    rval_txt = response.content.decode("utf-8")
    logging.debug(rval_txt)
    rval = json.loads(rval_txt)
    logging.debug(json.dumps(rval, indent=2))
    name = rval["name"]
    ghr_page = rval["ghr_page"]
    genes = rval["related-gene-list"] if "related-gene-list" in rval else []
    for gene in genes:
      df_this = pd.DataFrame({"id":[id_this], "name":[name],
	"gene-symbol":[gene["related-gene"]["gene-symbol"]],
	"ghr-page":[gene["related-gene"]["ghr-page"]]})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

##############################################################################
