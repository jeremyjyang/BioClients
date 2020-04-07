#!/usr/bin/env python3
"""
Access to Ensembl REST API.
http://rest.ensembl.org/documentation/info/lookup
"""
import sys,os,re,time,json,logging
import requests
#
##############################################################################
def GetInfo(base_url, ids, fout):
  n_gene=0; n_out=0; n_err=0; tags=[];
  for id_this in ids:
    url_this = base_url+'/lookup/id/'+id_this+'?content-type=application/json&expand=0'
    logging.debug(url_this)
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      logging.error('{0} : "{1}"'.format(rval.status_code, id_this))
      n_err+=1
      continue
    gene = rval.json()
    if not tags:
      for tag in gene.keys():
        if type(gene[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
      fout.write('\t'.join(tags)+'\n')
    n_gene+=1
    vals = [str(gene[tag]).replace('\n', ' ') if tag in gene and gene[tag] is not None else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_ids: {0}'.format(len(ids)))
  logging.info('n_gene: {0}'.format(n_gene))
  logging.info('n_out: {0}'.format(n_out))
  logging.info('n_err: {0}'.format(n_err))

##############################################################################
def GetXrefs(base_url, ids, fout):
  n_out=0; n_err=0; dbcounts={};
  tags = ['ensembl_id', 'xref_dbname', 'xref_id', 'xref_description']
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    url_this = base_url+'/xrefs/id/'+id_this
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      #rval.raise_for_status()
      logging.error('{0} : "{1}"'.format(rval.status_code, id_this))
      n_err+=1
      continue
    xrefs = rval.json()
    for xref in xrefs:
      if not (type(xref) is dict and 'dbname' in xref): continue
      dbname = xref['dbname']
      if dbname not in dbcounts: dbcounts[dbname]=0
      dbcounts[dbname]+=1
      vals = []
      for tag in ['dbname', 'primary_id', 'description']:
        vals.append(xref[tag] if tag in xref and xref[tag] is not None else '')
      fout.write('\t'.join([id_this]+vals)+'\n')
      n_out+=1
  for key in sorted(dbcounts.keys()):
    logging.info('Xref counts, db = %12s: %5d'%(key, dbcounts[key]))
  logging.info('n_ids: %d'%(len(ids)))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))
#
##############################################################################
