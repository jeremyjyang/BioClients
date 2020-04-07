#!/usr/bin/env python3
"""
Access to Ensembl REST API.
http://rest.ensembl.org/documentation/info/lookup
"""
import sys,os,re,time,json,logging
import requests
#
##############################################################################
def ShowVersion(base_url, fout):
  rest_api_ver = requests.get(base_url+'/info/rest?content-type=application/json').json()['release']
  sw_api_ver = requests.get(base_url+'/info/software?content-type=application/json').json()['release']
  eg_ver = requests.get(base_url+'/info/eg_version?content-type=application/json').json()['version']
  fout.write("EnsEMBL REST API version: {0}; EnsEMBL software API version: {1}; EnsEMBL genomes version: {2}\n".format(rest_api_ver, sw_api_ver, eg_ver))

##############################################################################
def ListSpecies(base_url, fout):
  n_out=0; tags=None;
  rval = requests.get(base_url+'/info/species?content-type=application/json').json()
  specs = rval["species"]
  for spec in specs:
    if not tags:
      tags = spec.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(spec[tag]) if tag in spec else "") for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_out: {0}'.format(n_out))

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
  logging.info('n_ids: {0}; n_gene: {1}; n_out: {2}; n_err: {3}'.format(len(ids), n_gene, n_out, n_err))

##############################################################################
def GetXrefs(base_url, ids, fout):
  n_out=0; n_err=0; tags=None; dbcounts={};
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
      if not tags:
        tags = list(xref.keys())
        fout.write('\t'.join(["id"]+tags)+'\n')
      vals = [(str(xref[tag]) if tag in xref else '') for tag in tags]
      fout.write('\t'.join([id_this]+vals)+'\n')
      n_out+=1
  for key in sorted(dbcounts.keys()):
    logging.info('Xref counts, db = %12s: %5d'%(key, dbcounts[key]))
  logging.info('n_ids: {0}; n_out: {1}; n_err: {2}'.format(len(ids), n_out, n_err))

##############################################################################
