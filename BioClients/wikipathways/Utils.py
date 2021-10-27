#!/usr/bin/env python3
##############################################################################
### Utilities for Wikipathways REST API.
### See: http://www.wikipathways.org/index.php/Help:WikiPathways_Webservice/API
##############################################################################
import sys,os,re,time,logging
import urllib.parse
#
from ..util import rest
#
##############################################################################
def ListOrganisms(base_url, fout):
  n_all=0; n_out=0; n_err=0;
  url=base_url+'/listOrganisms?format=json'
  rval=rest.GetURL(url, parse_json=True)
  organisms = rval['organisms']
  fout.write('Organism\n')
  for organism in organisms:
    fout.write('%s\n'%(organism))
    n_out+=1
  logging.info('n_out: %d'%(n_out))

##############################################################################
def ListPathways(base_url, params, fout):
  n_all=0; n_out=0; n_err=0;
  url = base_url+'/listPathways?format=json'
  if params['human']:
    url+=('&organism=%s'%urllib.parse.quote('Homo sapiens'))
  rval=rest.GetURL(url, parse_json=True)
  pathways = rval['pathways']
  tags=[];
  for pathway in pathways:
    n_all+=1
    if n_all==1 or not tags:
      tags = sorted(pathway.keys())
      fout.write('\t'.join(tags)+'\n')
    vals = [pathway[tag] if tag in pathway else '' for tag in tags]
    fout.write((','.join(vals))+'\n')
    n_out+=1
  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all,n_out,n_err))

##############################################################################
def GetPathway(base_url, id_query, ofmt, fout):
  n_all=0; n_out=0; n_err=0;
  if ofmt.lower() == 'gpml':
    url = base_url+'/getPathway?pwId=%s&revision=0'%id_query
  else:
    url = base_url+'/index.php?method=getPathwayAs&fileType=%s&pwId=%s&revision=0'%(ofmt.lower(), id_query)
  rval = rest.GetURL(url, parse_json=False)
  fout.write(rval)

