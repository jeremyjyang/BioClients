#!/usr/bin/env python3
###
import sys,os,json,re,logging,tqdm,requests,urllib.parse
import pandas as pd
#
API_HOST="icite.od.nih.gov"
API_BASE_PATH="/api/pubs"
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100;
#
#############################################################################
def GetStats(pmids, base_url=BASE_URL, fout=None):
  """Request multiply by chunk. Lists of PMIDs (e.g. references,
cited_by) reported as counts."""
  n_in=0; n_out=0; tags=None; df=pd.DataFrame(); tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  while True:
    if tq is None and not quiet: tq = tqdm.tqdm(total=len(pmids), unit="pmids")
    if n_in>=len(pmids): break
    pmids_this = pmids[n_in:n_in+NCHUNK]
    n_in += (NCHUNK if n_in+NCHUNK < len(pmids) else len(pmids)-n_in)
    url_this = (f"""{base_url}?pmids={(','.join(pmids_this))}""")
    response = requests.get(url_this)
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    url_self = result['links']['self']
    pubs = result['data']
    for pub in pubs:
      if not tags: tags = list(pub.keys())
      df_this = pd.DataFrame({tags[j]:[pub[tags[j]]] for j in range(len(tags))})
      if fout: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      df = pd.concat([df, df_this])
      n_out+=1
    if not quiet:
      for j in range(len(pmids_this)): tq.update()
  logging.info(f"n_in: {len(pmids)}; n_out: {n_out}")
  return df

#############################################################################
def GetStats_single(pmids, base_url=BASE_URL, fout=None):
  """Request singly."""
  tags=None; df=pd.DataFrame(); tq=None;
  for pmid in pmids:
    if tq is None: tq = tqdm.tqdm(total=len(pmids), unit="pmids")
    tq.update()
    url = base_url+'/'+pmid
    response = requests.get(url)
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    pub = response.json()
    if not tags: tags = list(pub.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[pub[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_in: {len(pmids)}; n_out: {df.shape[0]}")
  return df

#############################################################################
