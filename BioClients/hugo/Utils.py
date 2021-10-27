#!/usr/bin/env python3
"""
Utility functions for HUGO REST API.
See: http://www.genenames.org/help/rest-web-service-help
"""
import sys,os,re,json,time,logging
import pandas as pd

from ..util import rest
#
API_HOST='rest.genenames.org'
API_BASE_PATH=''
BASE_URL='http://'+API_HOST+API_BASE_PATH
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Accept':OFMTS['JSON']}
#
##############################################################################
def Info(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/info', headers=HEADERS, parse_json=True)
  logging.info(json.dumps(rval, sort_keys=True, indent=2))

##############################################################################
def ListSearchableFields(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/info', headers=HEADERS, parse_json=True)
  fields = rval['searchableFields'] if 'searchableFields' in rval else None
  fields.sort()
  df = pd.DataFrame({'fields':fields})
  if fout: df.to_csv(fout, "\t", index=False)
  return df

##############################################################################
def GetGenes(qrys, ftypes, skip=0, base_url=BASE_URL, fout=None):
  '''The API can return multiple hits for each query, though should not 
for exact SYMBOL fetch.  One case is for RPS15P5, status "Entry Withdrawn".'''
  n_in=0; n_found=0; n_notfound=0; n_ambig=0; n_gene=0;
  tags=[]; df=None;
  logging.debug('ftypes[{}]: {}'.format(len(ftypes), (','.join(ftypes))))
  for qry in qrys:
    n_in+=1
    if n_in<skip: continue
    logging.debug('{}. query: {}'.format(n_in, qry))
    numFound=0; genes=[];
    ftype_hit=None
    for ftype in ftypes:
      rval = rest.GetURL(base_url+'/fetch/{}/{}'.format(ftype.lower(), qry), headers=HEADERS, parse_json=True)
      if rval is None: continue
      ftype_hit=ftype
      responseHeader = rval['responseHeader']
      logging.debug('response status = {}'.format(responseHeader['status']))
      response = rval['response'] 
      numFound = response['numFound'] if 'numFound' in response else 0
      genes = response['docs']
      if numFound>0: break
    if numFound==0:
      n_notfound+=1
      logging.debug('Not found: {} = {}'.format(ftype_hit, qry))
      continue
    elif numFound>0:
      n_found+=1
    if len(genes)>1:
      logging.debug('Warning: multiple ({}) hits, {} = {} (Duplicate may be status=withdrawn.)'.format(len(genes), ftype_hit, qry))
      n_ambig+=1
    for gene in genes:
      if not tags: tags = list(gene.keys())
      data_this = {'query':qry, 'field':ftype_hit}
      data_this.update({tags[j]:[gene[tags[j]]] for j in range(len(tags))})
      df = pd.concat([df, pd.DataFrame(data_this)])
      n_gene+=1

  logging.info('queries: {}; found: {}; not found: {}; ambiguous: {}; total genes returned: {}'.format(n_in-skip, n_found, n_notfound, n_ambig, n_gene))
  if fout: df.to_csv(fout, "\t", index=False)
  return df

##############################################################################
def SearchGenes(qrys, ftypes, base_url=BASE_URL, fout=None):
  n_in=0; n_found=0; tags=[]; df=None;
  for qry in qrys:
    n_in+=1
    logging.debug('{}. query: {}'.format(n_in, qry))
    found_this=False
    for ftype in ftypes:
      url = (base_url+'/search{}/*{}*'.format((('/'+ftype.lower()) if ftype else ''), qry))
      rval = rest.GetURL(url, headers=HEADERS, parse_json=True)
      responseHeader = rval['responseHeader']
      logging.debug('response status = {}'.format(responseHeader['status']))
      response = rval['response'] 
      numFound = response['numFound'] if 'numFound' in response else 0
      if numFound==0: continue
      found_this=True
      docs = response['docs'] if 'docs' in response else []
      for doc in docs:
        logging.debug(json.dumps(doc, sort_keys=True, indent=2)+'\n')
        if not tags: tags = list(doc.keys())
        data_this = {'query':qry, 'field':ftype}
        data_this.update({tags[j]:[doc[tags[j]]] for j in range(len(tags))})
        df = pd.concat([df, pd.DataFrame(data_this)])
    if found_this: n_found+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {}; found: {}'.format(n_in, n_found))
  return df

