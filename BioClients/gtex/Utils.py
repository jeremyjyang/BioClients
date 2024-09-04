#!/usr/bin/env python3
"""
Utility functions for GTEx REST API.
https://www.gtexportal.org/home/api-docs

curl -X GET "https://gtexportal.org/rest/v1/metadata/dataset?format=json&sortBy=datasetId" -H "accept: application/json"
"""
###
import sys,os,re,json,collections,time,urllib.parse,logging,tqdm,tqdm.auto
import pandas as pd
import requests
#
NCHUNK=100
#
API_HOST="gtexportal.org"
API_BASE_PATH="/rest/v1"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def ListDatasets(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  response = requests.get(f"{base_url}/metadata/dataset?format=json&sortBy=datasetId", headers={"Content-Type":"application/json"})
  result = response.json()
  logging.debug(json.dumps(result, indent=2))
  datasets = result["dataset"]
  for dataset in datasets:
    logging.info(f"datasetId: {dataset['datasetId']}")
    if not tags: tags = [tag for tag in dataset.keys() if type(dataset[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tags[j]:[dataset[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListSubjects(datasetId, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; page=0;
  while True:
    url_this = f"{base_url}/dataset/subject?format=json&datasetId={datasetId}&pageSize={NCHUNK}&page={page}"
    response = requests.get(url_this, headers={"Content-Type":"application/json"})
    result = response.json()
    subjects = result["subject"]
    for subject in subjects:
      if not tags: tags = [tag for tag in subject.keys() if type(subject[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[subject[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    if "numPages" in result and result["numPages"]-1>page:
      page+=1
    else:
      break
  logging.info(f"n_out: {n_out}")
  return df
 
##############################################################################
def ListSamples(datasetId, subjectId, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; page=0;
  while True:
    url_this = f"{base_url}/dataset/sample?format=json&datasetId={datasetId}&subjectId={subjectId}&pageSize={NCHUNK}&page={page}"
    response = requests.get(url_this, headers={"Content-Type":"application/json"})
    result = response.json()
    samples = result["sample"]
    for sample in samples:
      if not tags: tags = [tag for tag in sample.keys() if type(sample[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[sample[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    if "numPages" in result and result["numPages"]-1>page:
      page+=1
    else:
      break
  logging.info(f"n_out: {n_out}")
  return df
 
##############################################################################
# https://gtexportal.org/rest/v1/expression/geneExpression?datasetId=gtex_v8&gencodeId=ENSG00000188906.14&format=json
def GetGeneExpression(ids, datasetId, skip, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for i in tqdm.auto.trange(len(ids), desc="IDs"):
    id_this = ids[i]
    response = requests.get(f"{base_url}/expression/geneExpression?datasetId=gtex_v8&gencodeId={id_this}&format=json", headers={"Content-Type":"application/json"})
    result = response.json()
    #logging.debug(json.dumps(result, indent=2))
    gexs = result["geneExpression"]
    for gex in gexs:
      if not tags: tags = [tag for tag in gex.keys() if type(gex[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tags[j]:[gex[tags[j]]] for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
