#!/usr/bin/env python3
'''
	GeneOntology client.
'''
import os,sys,re,json,time,logging
import urllib.parse

from ..util import rest_utils

#
##############################################################################
def GetEntities(base_url, ids, fout): 
  """For only one type of entity per call (gene, term)."""
  n_ent=0; tags=[];
  for id_this in ids:
    ent = rest_utils.GetURL(base_url+'/bioentity/%s'%(urllib.parse.quote(id_this)), parse_json=True)
    logging.debug(json.dumps(ent, sort_keys=True, indent=2))
    n_ent+=1
    if not tags:
      tags = ent.keys()
      fout.write('%s\n'%('\t'.join(tags)))
    vals = [str(ent[tag]) if tag in ent else '' for tag in tags]
    fout.write('%s\n'%('\t'.join(vals)))
  logging.info('n_ent: %d'%(n_ent))

##############################################################################
def GetGeneTerms(base_url, ids, fout): 
  n_assn=0; tags=[];
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/bioentity/gene/%s/function'%(urllib.parse.quote(id_this)), parse_json=True)
    assns = rval['associations'] if 'associations' in rval else []
    for assn in assns:
      logging.debug(json.dumps(assn, sort_keys=True, indent=2))
      n_assn+=1
      if not tags:
        tags = assn.keys()
        fout.write('%s\n'%('\t'.join(tags)))
      vals = [str(assn[tag]) if tag in assn else '' for tag in tags]
      fout.write('%s\n'%('\t'.join(vals)))
  logging.info('n_gene: %d; n_assn: %d'%(len(ids), n_assn))

##############################################################################
