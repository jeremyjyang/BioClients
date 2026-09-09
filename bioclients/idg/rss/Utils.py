#!/usr/bin/env python3
"""
IDG Resource Submission System
https://rss.ccs.miami.edu/
"""
###
import sys,os,re,json,time,logging,tqdm
import pandas as pd
import requests
import urllib,urllib.parse
#
#
API_HOST="rss.ccs.miami.edu"
API_BASE_PATH="/rss-api"
BASE_URL = 'https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def ListTargets(base_url=BASE_URL, fout=None):
  tags=[]; tq=None; df=pd.DataFrame(); 
  url = (base_url+f'/target')
  resp = requests.get(url, verify=False)
  targets = resp.json() if resp.status_code==200 else []
  for target in targets:
    logging.debug(json.dumps(target, sort_keys=True, indent=2))
    if not tags: tags = list(target.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(df.shape[0]))
  return(df)

##############################################################################
def GetTargetResources(ids, base_url=BASE_URL, fout=None):
  tags=[]; tq=None; df=pd.DataFrame();
  for id_this in ids:
    url_this = (base_url+f'/target/id?id={id_this}')
    resp = requests.get(url_this, verify=False)
    resources = resp.json() if resp.status_code==200 else []
    for resource in resources:
      logging.debug(json.dumps(resource, sort_keys=True, indent=2))
      if not tags: tags = list(resource.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[resource[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(df.shape[0]))
  return(df)

##############################################################################
