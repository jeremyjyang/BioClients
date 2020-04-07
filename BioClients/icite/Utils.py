#!/usr/bin/env python3
###
import sys,os,json,re,logging
#
from ..util import rest_utils

#############################################################################
def GetStats(base_url, pmids, fout):
  """Request multiply by chunk. Lists of PMIDs (e.g. references,
cited_by) reported as counts."""
  n_in=0; n_out=0; tags=None; nchunk=100;
  while True:
    if n_in>=len(pmids): break
    pmids_this = pmids[n_in:n_in+nchunk]
    n_in += (nchunk if n_in+nchunk < len(pmids) else len(pmids)-n_in)
    url_this = (base_url+'?pmids=%s'%(','.join(pmids_this)))
    rval = rest_utils.GetURL(url_this, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, indent=2))
    url_self = rval['links']['self']
    pubs = rval['data']
    for pub in pubs:
      if not tags:
        tags = list(pub.keys())
        fout.write('\t'.join(tags)+'\n')
      vals=[];
      for tag in tags:
        val = (pub[tag] if tag in pub else '')
        if type(val) is list: val = len(val)
        elif type(val) is float: val = "{:.3f}".format(val)
        vals.append(val)
      fout.write('\t'.join([str(val) for val in vals])+'\n')
      n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(pmids), n_out))

#############################################################################
def GetStats_single(base_url, pmids, fout):
  """Request singly."""
  n_out=0; tags=None;
  for pmid in pmids:
    url = base_url+'/%s'%pmid
    pub = rest_utils.GetURL(url, parse_json=True)
    if not pub:
      logging.info('not found: %s'%(pmid))
      continue
    if not tags:
      tags = pub.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(pub[tag]) if tag in pub else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(pmids), n_out))

#############################################################################
