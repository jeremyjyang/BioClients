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
  if fout: df.to_csv(fout, sep="\t", index=False)
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
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def GetInfo(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=[]; df=None; tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if tq is None and not quiet: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = base_url+'/lookup/id/'+id_this+'?content-type=application/json&expand=0'
    logging.debug(url_this)
    try:
      rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    except Exception as e:
      logging.error(f"{e}")
      n_err+=1
      continue
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{id_this}"')
      n_err+=1
      continue
    gene = rval.json()
    if not tags:
      for tag in gene.keys():
        if type(gene[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
    df_this = pd.DataFrame({tags[j]:([str(gene[tags[j]])] if tags[j] in gene else ['']) for j in range(len(tags))})
    if fout is not None:
      df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += 1
    if fout is None: df = pd.concat([df, df_this])
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_ids: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  if fout is None: return df

##############################################################################
def GetXrefs(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; dbcounts={}; df=pd.DataFrame(); tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if tq is None and not quiet: tq = tqdm.tqdm(total=len(ids)-skip)
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
      df_this =  pd.DataFrame({tags[j]:([str(xref[tags[j]])] if tags[j] in xref else ['']) for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False)
      n_out+=1
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  for key in sorted(dbcounts.keys()):
    logging.info(f"Xref counts, db = {key:12s}: {dbcounts[key]:5d}")
  logging.info(f"n_ids: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  if fout is None: return df

##############################################################################
def GetVariantEffectPredictions(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tags=None; tags_tc=None; dbcounts={}; df=pd.DataFrame(); tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if tq is None and not quiet: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = base_url+'/vep/human/id/'+id_this
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{id_this}"')
      n_err+=1
      continue
    result = rval.json()
    if not result or len(result)==0:
      logging.error(f"No result.")
      n_err+=1
      continue
    vep = result[0]
    logging.debug(json.dumps(vep, indent=2))
    if not tags:
      tags = [tag for tag in vep.keys() if type(vep[tag]) not in (list, dict)] #Only simple metadata.
    df_this_base = pd.DataFrame({tags[j]:([str(vep[tags[j]])] if tags[j] in vep else ['']) for j in range(len(tags))})
    transcript_consequences = vep["transcript_consequences"] if "transcript_consequences" in vep else []
    #colocated_variants = vep["colocated_variants"] if "colocated_variants" in vep else []
    for tc in transcript_consequences:
      if not tags_tc:
        tags_tc = [tag for tag in tc.keys() if type(tc[tag]) not in (list, dict)] #Only simple metadata.
      logging.debug(f"tags_tc: {tags_tc}")
      df_this_tc = pd.DataFrame({tag:([str(tc[tag])] if tag in tc else ['']) for tag in tags_tc})
      df_this = pd.concat([df_this_base, df_this_tc], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False)
      n_out+=1
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_ids: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  if fout is None: return df

##############################################################################
