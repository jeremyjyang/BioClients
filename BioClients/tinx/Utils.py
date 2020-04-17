#!/usr/bin/env python3
"""
TIN-X (Target Importance and Novelty Explorer) REST API client
https://www.newdrugtargets.org/
https://api.newdrugtargets.org/docs
https://api.newdrugtargets.org/targets/
"""
###
import sys,os,re,json,time,logging
import urllib,urllib.parse
#
from ..util import rest_utils
#
NCHUNK=10;
#
##############################################################################
def ListTargets(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/targets/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags:
        tags = list(target.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(target[tag]) if tag in target else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def ListDiseases(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/diseases/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags:
        tags = list(disease.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(disease[tag]) if tag in disease else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

