#!/usr/bin/env python3
"""
Utility functions for BioGRID REST API.
See: http://wiki.thebiogrid.org/doku.php/biogridrest
"""
###
import sys,os,re,json,time,logging,yaml
#
from ..util import rest_utils
#
##############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

##############################################################################
def ListOrganisms(base_url, params, fout):
  n_all=0; n_out=0; n_err=0;
  url=base_url+'/organisms/?accesskey=%s'%params['API_KEY']
  url+=('&format=tab2')
  rval=rest_utils.GetURL(url, parse_json=False)
  txt = rval
  lines = txt.splitlines()
  fout.write('organism_id, organism"\n')
  for line in lines:
    oid,org = re.split('\t', line)
    fout.write('%s\t"%s"\n'%(oid, org))
    n_out+=1
  logging.info('n_out: %d'%(n_out))

##############################################################################
def ListIdTypes(base_url, params, fout):
  n_all=0; n_out=0; n_err=0;
  url=base_url+'/identifiers/?accesskey=%s'%params['API_KEY']
  url+=('&format=tab2')
  rval=rest_utils.GetURL(url, parse_json=False)
  txt = rval
  lines = txt.splitlines()
  for line in lines:
    fout.write('%s\n'%(line))
    n_all+=1
    n_out+=1
  logging.info('n_out: %d'%(n_out))

##############################################################################
def GetInteractions(base_url, params, ids, fout):
  n_all=0; n_out=0; n_err=0;
  t0=time.time()
  tags=[];

  for iid in ids:
    url=base_url+'/interactions/%s?'%iid
    url+=('&accesskey=%s&format=json'%params['API_KEY'])
    rval=rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2, sort_keys=False)+'\n')

    if type(rval) is not dict:
      n_err+=1
      continue
    if not iid in rval :
      n_err+=1
      continue
    intr = rval[iid]
    n_all+=1

    if n_all==1 or not tags:
      tags=intr.keys()
      fout.write('\t'.join(tags)+'\n')

    vals=[intr[tag] if tag in intr else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all, n_out, n_err))

##############################################################################
def SearchInteractions(base_url, params, ids, search_params, fout):
  n_all=0; n_out=0; n_err=0;
  t0=time.time()
  tags=[];

  url=base_url+('/interactions/?accesskey=%s&format=json'%params['API_KEY'])
  if ids:
    url+=('&geneList=%s'%('|'.join(ids)))
  url+=('&interSpeciesExcluded=%s'%str(not search_params['inc_interspecies']).lower())
  url+=('&selfInteractionsExcluded=%s'%str(not search_params['inc_self']).lower())
  if search_params['elist']:
    url+=('&includeEvidence=%s'%str(search_params['inc_evidence']).lower())
    url+=('&evidenceList=%s'%('|'.join(search_params['elist'])))
  if search_params['addl_idtypes']:
    url+=('&additionalIdentifierTypes=%s'%('|'.join(search_params['addl_idtypes'])))
  if search_params['human']:
    url+=('&taxId=9606')

  skip=0; chunk=1000;

  while True:
    url_this=url+('&start=%d&max=%d'%(skip, chunk))
    rval=rest_utils.GetURL(url_this, parse_json=True)
    logging.debug(json.dumps(rval, indent=2, sort_keys=False)+'\n')
    if not rval: break
    if type(rval) is not dict:
      n_err+=1
      continue
    intrs = rval
    for iid, intr in intrs.items():
      n_all+=1
      if n_all==1 or not tags:
        tags=intr.keys()
        fout.write('\t'.join(tags)+'\n')
      vals=[];
      for tag in tags:
        vals.append(intr[tag] if tag in intr else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    skip+=chunk

  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all, n_out, n_err))
  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

##############################################################################
