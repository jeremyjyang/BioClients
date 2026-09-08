#!/usr/bin/env python3
##############################################################################
### Utility functions for access to TINX REST API.
### 
### https://tinx-api.shishito.health.unm.edu/docs/
##############################################################################
import sys,os,re,json,logging
#
import urllib.parse,requests,tqdm
import pandas as pd
#
API_HOST='tinx-api.shishito.health.unm.edu'
API_BASE_PATH='/'
#
NCHUNK=25
N_MAX_HIT=100
#
#############################################################################
def GetDiseaseTargets(ids, n_max_hit, base_url, fout):
  n_out=0; n_err=0; df=None; tags=None; tags_tgt=None;
  headers = { "accept": "application/json" }

  for id_this in ids:
    tq=None;
    offset=0; n_total=None; url_next=None;
    while True:
      if n_total and offset>n_total:
        break
      url_this = url_next if url_next else f"{base_url}/diseases/{urllib.parse.quote(id_this)}/targets/?offset={offset}&limit={NCHUNK}"
      response = requests.get(url_this, headers=headers)
      result = response.json()
      logging.debug(json.dumps(result, sort_keys=True, indent=2))
      if not response.ok or response.status_code != 200:
        response.raise_for_status()
        logging.error(f"status_code: {response.status_code}")
        n_err+=1
        break
      n_total = result['count'] if 'count' in result else None
      if not n_total: break
      if tq is None: tq = tqdm.tqdm(total=min(n_total, n_max_hit))

      url_next = result['next'] if 'next' in result else None

      things = result['results'] if 'results' in result else []

      for thing in things:
        if not tags:
          tags = list(thing.keys())
          for tag in tags[:]:
            if type(thing[tag]) in (list, dict):
              tags.remove(tag)
        df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
        target = thing['target'] if 'target' in thing else {}
        if not tags_tgt:
          tags_tgt = list(target.keys())
          for tag in tags_tgt[:]:
            if type(target[tag]) in (list, dict):
              tags_tgt.remove(tag)
        df_this_tgt = pd.DataFrame({tag:[target[tag] if tag in target else ''] for tag in tags_tgt})
        df_this = pd.concat([df_this, df_this_tgt], axis=1)

        if fout is not None:
          df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        else:
          df = pd.concat([df, df_this])
        n_out += df_this.shape[0]
        tq.update(df_this.shape[0])
        if n_out>=n_max_hit: break
      if n_out>=n_max_hit: break
      offset += NCHUNK
    tq.close()

  logging.info(f"n_in: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  return df

#############################################################################
def GetTargetDiseases(ids, n_max_hit, base_url, fout):
  n_out=0; n_err=0; df=None; tags=None; tags_dis=None;
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_url}/targets/{urllib.parse.quote(id_this)}/diseases/", headers=headers)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue
    things = result['results'] if 'results' in result else []

    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
      disease = thing['disease'] if 'disease' in thing else {}
      if not tags_dis:
        tags_dis = list(disease.keys())
        for tag in tags_dis[:]:
          if type(disease[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags_dis.remove(tag)
      df_this_dis = pd.DataFrame({tag:[disease[tag] if tag in disease else ''] for tag in tags_dis})
      df_this = pd.concat([df_this, df_this_dis], axis=1)
      if fout is not None:
        df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        n_out += 1
      if fout is None: df = pd.concat([df, df_this])

  logging.info(f"n_in: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  return df

#############################################################################
