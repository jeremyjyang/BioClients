#!/usr/bin/env python3
"""
https://stitcher.ncats.io/api/stitches/latest/8R78F6L9VO
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='stitcher.ncats.io'
API_BASE_PATH='/api/stitches'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100
#
##############################################################################
def GetDrug(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url_this = f"{base_url}/latest/{id_this}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: continue
    thing = response.json()
    if not tags:
      tags = list(thing.keys())
      for tag in tags[:]:
        if type(thing[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
    df_this = pd.concat([
        df_this,
        pd.DataFrame({
            "unii":[id_this],
            "labels":[str(thing['labels']) if 'labels' in thing else ''],
	        "datasource_id":[thing['datasource']['id'] if 'datasource' in thing and 'id' in thing['datasource'] else '']})
        ], axis=1)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetDrugTargets(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url_this = f"{base_url}/latest/{id_this}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: continue
    thing = response.json()

    df_drug = pd.DataFrame({
            'unii':[id_this],
            'id':[thing['id'] if 'id' in thing else ''],
            })

    sgroup = thing['sgroup'] if 'sgroup' in thing else {}
    properties = sgroup['properties'] if 'properties' in sgroup else {}
    targets = properties['TARGETS'] if 'TARGETS' in properties else []

    if not targets:
      logging.info(f"No targets found for UNII: {id_this}")
      continue

    for target in targets:
      target_value = target['value'] if 'value' in target else ''
      tvs = re.split(r'\|', target_value)
      tv1 = tvs[0] if len(tvs)>0 else ''
      tv2 = tvs[1] if len(tvs)>1 else ''
      tv3 = tvs[2] if len(tvs)>2 else ''
      tv4 = tvs[3] if len(tvs)>3 else ''
      tv5 = tvs[4] if len(tvs)>4 else ''
      tv6 = tvs[5] if len(tvs)>5 else ''

      df_this = pd.concat([
        df_drug,
        pd.DataFrame({
	        "target_node":[target['node'] if 'node' in target else ''],
                     "target_value_1":[tv1],
                     "target_value_2":[tv2],
                     "target_value_3":[tv3],
                     "target_value_4":[tv4],
                     "target_value_5":[tv5],
                     "target_value_6":[tv6],
                     }
                     )
        ], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df
