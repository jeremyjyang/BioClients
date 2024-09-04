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
import requests,urllib,urllib.request,urllib.parse
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
    url_this = f"{base_url}/json/get_string_ids?identifier={id_this}"
    response = requests.get(url_this)
    results = response.json()
    for result in results:
      logging.debug(result)
      if not tags: tags = list(result.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"queries: {len(ids)}; results: {df.shape[0]}")
  return df

##############################################################################
def GetInteractionPartners(ids, species, limit, minscore, base_url=BASE_URL, fout=None):
  """ALL interacting proteins, up to limit (ordered by confidence)"""
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    url_this = f"{base_url}/json/interaction_partners?identifier={id_this}"
    if species: url_this+=(f'&species={species}')
    if limit: url_this+=(f'&limit={limit}')
    if minscore: url_this+=(f'&required_score={minscore}')
    response = requests.get(url_this)
    results = response.json()
    for result in results:
      logging.debug(result)
      if not tags: tags = list(result.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"queries: {len(ids)}; interaction partners: {df.shape[0]}")
  return df

##############################################################################
def GetEnrichment(ids, species, minscore, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  ids_param = urllib.parse.quote('\n'.join(ids))
  url = f"{base_url}/json/enrichment?identifiers={ids_param}"
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  response = requests.get(url)
  results = response.json()
  for result in results:
    logging.debug(result)
    if not tags: tags = list(result.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"queries: {len(ids)}; enrichment results: {df.shape[0]}")
  return df

##############################################################################
def GetPPIEnrichment(ids, species, minscore, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  ids_param = urllib.parse.quote('\n'.join(ids))
  url = f"{base_url}/json/ppi_enrichment?identifiers={ids_param}"
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  response = requests.get(url)
  results = response.json()
  for result in results:
    logging.debug(result)
    if not tags: tags = list(result.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[result[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"queries: {len(ids)}; enrichment results: {df.shape[0]}")
  return df

##############################################################################
def GetNetwork(nid, species, minscore, netflavor, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  url = base_url+f'/json/network?identifier={nid}'
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  if netflavor: url+=(f'&network_flavor={netflavor}')
  response = requests.get(url)
  edges = response.json()
  logging.debug(json.dumps(edges, indent=2))
  for edge in edges:
    logging.debug(edge)
    if not tags: tags = list(edge.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[edge[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"edges: {df.shape[0]}")
  return df

##############################################################################
def GetNetworkImage(nid, species, minscore, netflavor, imgfmt, base_url=BASE_URL, fout=None):
  """image, highres_image, or svg"""
  url = base_url+f'/{imgfmt}/network?identifier={nid}'
  if species: url+=(f'&species={species}')
  if minscore: url+=(f'&required_score={minscore}')
  if netflavor: url+=(f'&network_flavor={netflavor}')
  response = requests.get(url)
  img = response.content
  if fout is not None:
    fout.write(img)
    fout.close()
  return img

##############################################################################
