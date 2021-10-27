#!/usr/bin/env python3
#############################################################################
### CDC  REST API client
### https://tools.cdc.gov/api/docs/info.aspx
### https://tools.cdc.gov/api/v2/resources
#############################################################################
import sys,os,re,json,csv,logging
import urllib.parse,requests
#
from ..util import rest
#
#############################################################################
def ListResources(base_url, resource, fout):
  tags=None; n_rsc=0; offset=0; nchunk=100;
  url=base_url+'/%s'%resource
  while True:
    url_this='%s?offset=%d&max=%d'%(url, offset, nchunk)
    rval=rest.GetURL(url_this, parse_json=True)
    try:
      rscs = rval['results']
      pag = rval['meta']['pagination']
      count = pag['count']
      total = pag['total']
      nextUrl = pag['nextUrl']
    except:
      break
    for rsc in rscs:
      if not tags:
        tags=rsc.keys()
        fout.write('\t'.join(tags)+'\n')
      vals = [str(rsc[tag]) if tag in rsc else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_rsc+=1
    if count>=total or not nextUrl:
      break
    else:
      offset+=nchunk
  logging.info('n_rsc = %d (total %s)'%(n_rsc, resource))

#############################################################################
