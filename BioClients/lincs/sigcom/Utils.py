#!/usr/bin/env python3
#############################################################################
### https://maayanlab.cloud/sigcom-lincs/#/API
#############################################################################
import sys,os,re,json,requests,tqdm,logging
import pandas as pd
import urllib.parse
#
API_HOST="maayanlab.cloud"
API_BASE_PATH="/sigcom-lincs/metadata-api"
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
#############################################################################
def GetResources(ids, base_url=BASE_URL, fout=None):
  tags=None; df=None;
  url_base = (base_url+'/resources')
  for id_this in ids:
    url = f"{url_base}/{urllib.parse.quote(id_this)}"
    response = requests.get(url)
    rval = response.json()
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
    res = rval
    df = pd.concat([df, pd.DataFrame({tags[j]:[res[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  return df

#############################################################################
