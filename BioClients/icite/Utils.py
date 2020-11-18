#!/usr/bin/env python3
###
import sys,os,json,re,logging
import pandas as pd
#
from ..util import rest
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
  n_in=0; n_out=0; tags=None; df=pd.DataFrame();
  while True:
    if n_in>=len(pmids): break
    pmids_this = pmids[n_in:n_in+NCHUNK]
    n_in += (NCHUNK if n_in+NCHUNK < len(pmids) else len(pmids)-n_in)
    url_this = (base_url+'?pmids={}'.format(','.join(pmids_this)))
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, indent=2))
    url_self = rval['links']['self']
    pubs = rval['data']
    for pub in pubs:
      if not tags: tags = list(pub.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[pub[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(pmids), df.shape[0]))
  return df

#############################################################################
def GetStats_single(pmids, base_url=BASE_URL, fout=None):
  """Request singly."""
  tags=None; df=pd.DataFrame();
  for pmid in pmids:
    url = base_url+'/'+pmid
    pub = rest.Utils.GetURL(url, parse_json=True)
    if not pub:
      logging.info('not found: %s'%(pmid))
      continue
    if not tags: tags = list(pub.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[pub[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(pmids), df.shape[0]))
  return df

#############################################################################
