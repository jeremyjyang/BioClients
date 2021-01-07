#!/usr/bin/env python3
"""
Access to Ensembl REST API.
http://rest.ensembl.org/documentation/info/lookup
"""
import sys,os,re,time,json,logging,tqdm
import pandas as pd
import requests
#
API_HOST='rest.ensembl.org'
API_BASE_PATH=''
#
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def ShowVersion(base_url=BASE_URL, fout=None):
  df = pd.DataFrame({
      "param": ["EnsEMBL REST API version", "EnsEMBL software API version", "EnsEMBL genomes version"],
      "value": [
          requests.get(base_url+'/info/rest?content-type=application/json').json()['release'],
          requests.get(base_url+'/info/software?content-type=application/json').json()['release'],
          requests.get(base_url+'/info/eg_version?content-type=application/json').json()['version']
          ]})
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def ListSpecies(base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  rval = requests.get(base_url+'/info/species?content-type=application/json').json()
  specs = rval["species"]
  for spec in specs:
    if not tags: tags = list(spec.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[spec[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def GetInfo(ids, base_url=BASE_URL, fout=None):
  n_err=0; tags=[]; df=pd.DataFrame(); tq=None;
  for id_this in ids:
    if tq is not None: tq.update()
    url_this = base_url+'/lookup/id/'+id_this+'?content-type=application/json&expand=0'
    logging.debug(url_this)
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{id_this}"')
      n_err+=1
      continue
    gene = rval.json()
    if not tags:
      for tag in gene.keys():
        if type(gene[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
    df = pd.concat([df, pd.DataFrame({tags[j]:([str(gene[tags[j]])] if tags[j] in gene else ['']) for j in range(len(tags))})])
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="genes")
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_ids: {len(ids)}; n_out: {df.shape[0]}; n_err: {n_err}")
  return df

##############################################################################
def GetXrefs(ids, base_url=BASE_URL, fout=None):
  n_err=0; tags=None; dbcounts={}; df=pd.DataFrame(); tq=None;
  for id_this in ids:
    if tq is not None: tq.update()
    url_this = base_url+'/xrefs/id/'+id_this
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{id_this}"')
      n_err+=1
      continue
    xrefs = rval.json()
    for xref in xrefs:
      if not (type(xref) is dict and 'dbname' in xref): continue
      dbname = xref['dbname']
      if dbname not in dbcounts: dbcounts[dbname]=0
      dbcounts[dbname]+=1
      if not tags: tags = list(xref.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:([str(xref[tags[j]])] if tags[j] in xref else ['']) for j in range(len(tags))})])
      n_out+=1
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="genes")
  for key in sorted(dbcounts.keys()):
    logging.info(f"Xref counts, db = {key:12s}: {dbcounts[key]:5d}")
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_ids: {len(ids)}; n_out: {df.shape[0]}; n_err: {n_err}")
  return df

##############################################################################
