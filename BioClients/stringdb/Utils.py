#!/usr/bin/env python3
"""
Utility for STRING Db REST API.

STRING = Search Tool for the Retrieval of Interacting Genes/Proteins

See: http://string-db.org/help/api/

http://[database]/[access]/[format]/[request]?[parameter]=[value]

database:
string-db.org
string.embl.de
stitch.embl.de
"""
###
import sys,os,re,json,time,logging
import pandas as pd
import urllib,urllib.request,urllib.parse
#
from ..util import rest
#
API_HOST='string-db.org'
API_BASE_PATH='/api'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NETWORK_FLAVORS=['evidence', 'confidence', 'actions']
IMG_FMTS=['image', 'highres_image', 'svg']
#
##############################################################################
def GetIds(ids, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    url_this = base_url+f'/json/get_string_ids?identifier={id_this}'
    results = rest.GetURL(url_this, parse_json=True)
    for result in results:
      logging.debug(result)
      if not tags: tags = list(result.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {} ; results: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetInteractionPartners(ids, species, minscore, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    url_this = base_url+f'/json/interaction_partners?identifier={id_this}'
    if species: url_this+=(f'&species={species}')
    if minscore: url_this+=(f'&required_score={minscore}')
    results = rest.GetURL(url_this, parse_json=True)
    for result in results:
      logging.debug(result)
      if not tags: tags = list(result.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {} ; interaction partners: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetEnrichment(ids, species, minscore, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  url = base_url+'/json/enrichment?identifiers={}'.format(urllib.parse.quote('\n'.join(ids)))
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  results = rest.GetURL(url, parse_json=True)
  for result in results:
    logging.debug(result)
    if not tags: tags = list(result.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {} ; enrichment results: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetPPIEnrichment(ids, species, minscore, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  url = base_url+'/json/ppi_enrichment?identifiers={}'.format(urllib.parse.quote('\n'.join(ids)))
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  results = rest.GetURL(url, parse_json=True)
  for result in results:
    logging.debug(result)
    if not tags: tags = list(result.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {} ; enrichment results: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetNetwork(nid, species, minscore, netflavor, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  url = base_url+f'/json/network?identifier={nid}'
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  if netflavor: url+=(f'&network_flavor={netflavor}')
  edges = rest.GetURL(url, parse_json=True)
  logging.debug(json.dumps(edges, indent=2))
  for edge in edges:
    logging.debug(edge)
    if not tags: tags = list(edge.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[edge[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('edges: {}'.format(df.shape[0]))
  return df

##############################################################################
def GetNetworkImage(nid, species, minscore, netflavor, imgfmt, base_url=BASE_URL):
  url = base_url+f'/{imgfmt}/network?identifier={nid}'
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  if netflavor: url+=(f'&network_flavor={netflavor}')
  img = rest.GetURL(url, parse_json=False, parse_xml=False)
  return img

##############################################################################
def GetInteractors(pids, species, minscore, base_url=BASE_URL, fout=None):
  """2018: May be deprecated since 2015."""
  tags=[]; df=pd.DataFrame();
  url=base_url+'/tsv/interactors'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; interactors: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetActions(pids, species, minscore, base_url=BASE_URL, fout=None):
  """2018: May be deprecated since 2015."""
  tags=[]; df=pd.DataFrame();
  url=base_url+'/tsv/actions'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; actions: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetAbstracts(pids, species, base_url=BASE_URL, fout=None):
  """2018: May be deprecated since 2015."""
  tags=[]; df=pd.DataFrame();
  url=base_url+'/tsv/abstracts'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  rval=rest.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; abstracts: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
