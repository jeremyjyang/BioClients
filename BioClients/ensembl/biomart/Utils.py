#!/usr/bin/env python3
"""
Access to Ensembl biomart REST API.
https://m.ensembl.org/info/data/biomart/biomart_restful.html
"""
import sys,os,re,time,json,logging,tqdm,io
import pandas as pd
import requests, urllib.parse
#
API_HOST='www.ensembl.org'
API_BASE_PATH='/biomart/martservice'
#
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def XMLQuery(xmltxt, base_url=BASE_URL, fout=None):
  url_this = base_url+f"?query={urllib.parse.quote(xmltxt)}"
  logging.debug(url_this)
  rval = requests.get(url_this)
  if not rval.ok:
    logging.error(f"{rval.status_code}")
  df = pd.read_table(io.StringIO(rval.text), "\t")
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"Output rows: {df.shape[0]}; cols: {df.shape[1]} ({str(df.columns.tolist())})")
  return df

##############################################################################
