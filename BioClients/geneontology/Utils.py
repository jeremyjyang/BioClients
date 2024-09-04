#!/usr/bin/env python3
"""
GeneOntology client.
"""
import os,sys,re,json,time,logging
import urllib.parse
import pandas as pd

from ..util import rest

API_HOST='api.geneontology.org'
API_BASE_PATH='/api'
BASE_URL = 'https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def GetEntities(ids, base_url=BASE_URL, fout=None): 
  """For only one type of entity per call (gene, term)."""
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    ent = rest.GetURL(base_url+'/bioentity/'+urllib.parse.quote(id_this), parse_json=True)
    logging.debug(json.dumps(ent, sort_keys=True, indent=2))
    if not tags: tags = ent.keys()
    df = pd.concat([df, pd.DataFrame({tags[j]:[ent[tags[j]]] for j in range(len(tags))})])
  logging.info('n_ent: {}'.format(df.shape[0]))
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
def GetGeneTerms(ids, base_url=BASE_URL, fout=None): 
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    rval = rest.GetURL(base_url+'/bioentity/gene/{}/function'.format(urllib.parse.quote(id_this)), parse_json=True)
    assns = rval['associations'] if 'associations' in rval else []
    for assn in assns:
      logging.debug(json.dumps(assn, sort_keys=True, indent=2))
      if not tags: tags = assn.keys()
      df = pd.concat([df, pd.DataFrame({tags[j]:[assn[tags[j]]] for j in range(len(tags))})])
  logging.info('n_gene: {}; n_assn: {}'.format(len(ids), df.shape[0]))
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
