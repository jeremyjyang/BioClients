#!/usr/bin/env python3
"""
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='gsrs.ncats.nih.gov'
API_BASE_PATH='/ginas/app/api/v1'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100
#
##############################################################################
def ListVocabularies(base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; tags_term=None; df=None;
  size=NCHUNK; skip=0;
  while True:
    url_this = f"{base_url}/vocabularies?skip={skip}&top={size}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: break
    results = response.json()
    things = results['content']
    if not things: break
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      for term in thing['terms']:
        if not tags_term:
          tags_term = list(term.keys())
        df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
        df_this = pd.concat([df_this, pd.DataFrame({f"term_{tag}":[term[tag] if tag in term else ''] for tag in tags_term})], axis=1)
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        n_out += df_this.shape[0]
    if results['count']<NCHUNK: break
    skip+=NCHUNK
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListSubstances(base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None; tq=None;
  size=NCHUNK; skip=0;
  while True:
    url_this = f"{base_url}/substances?skip={skip}&top={size}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: break
    results = response.json()
    if not tq: tq = tqdm.tqdm(total=results['total'])
    things = results['content']
    if not things: break
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    tq.update(n=results['count'])
    if results['count']<NCHUNK: break
    skip+=NCHUNK
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def Search(query, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  size=NCHUNK; skip=0;
  url_this = f"{base_url}/substances/search?q={urllib.parse.quote(query)}&top={size}"
  while True:
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: break
    results = response.json()
    things = results['content']
    if not things: break
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
      df_this = pd.concat([df_this,
pd.DataFrame({
	"struct_id":[thing['structure']['id'] if 'structure' in thing and 'id' in thing['structure'] else ''],
	"struct_smiles":[thing['structure']['smiles'] if 'structure' in thing and 'smiles' in thing['structure'] else '']})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    if results['count']<NCHUNK: break
    url_this = results['nextPageUri']
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetSubstance(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url_this = f"{base_url}/substances({id_this})"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: continue
    thing = response.json()
    if not tags:
      tags = list(thing.keys())
      for tag in tags[:]:
        if type(thing[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          tags.remove(tag)
    df_this = pd.DataFrame({tag:[thing[tag] if tag in thing else ''] for tag in tags})
    df_this = pd.concat([df_this,
	pd.DataFrame({
	"struct_id":[thing['structure']['id'] if 'structure' in thing and 'id' in thing['structure'] else ''],
	"struct_smiles":[thing['structure']['smiles'] if 'structure' in thing and 'smiles' in thing['structure'] else '']})], axis=1)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetSubstanceNames(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url_this = f"{base_url}/substances({id_this})/names"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: continue
    names = response.json()
    for name in names:
      if not tags:
        tags = list(name.keys())
        for tag in tags[:]:
          if type(name[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[name[tag] if tag in name else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
