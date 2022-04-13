#!/usr/bin/env python3
"""
LINCS REST API client
New (2019) iLINCS: 
http://www.ilincs.org/ilincs/APIinfo
http://www.ilincs.org/ilincs/APIdocumentation
(http://lincsportal.ccs.miami.edu/dcic/api/ DEPRECATED?)
"""
###
import sys,os,re,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST="www.ilincs.org"
API_BASE_PATH="/api"
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
#############################################################################
def GetGene(ids, base_url=BASE_URL, fout=None):
  tags=None; df=None;
  for id_this in ids:
    url = base_url+'/GeneInfos/'+id_this
    response = requests.get(url)
    rval = response.json()
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
    gene = rval
    df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  return df

#############################################################################
def GetDataset(ids, base_url=BASE_URL, fout=None):
  tags=None; df=None;
  for id_this in ids:
    url = base_url+'/PublicDatasets/'+id_this
    response = requests.get(url)
    rval = response.json()
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
    dset = rval
    df = pd.concat([df, pd.DataFrame({tag:[dset[tag]] for tag in tags})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  return df

#############################################################################
def GetCompound(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; tq=None;
  for id_this in ids:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="compounds")
    url = f"{base_url}/Compounds/{id_this}"
    response = requests.get(url)
    compound = response.json()
    logging.debug(json.dumps(compound, indent=2))
    if not tags:
      tags = list(compound.keys())
      for tag in tags[:]:
        if type(compound[tag]) in (list, dict):
          tags.remove(tag)
          logging.info(f"Ignoring tag \"{tag}\"")
    df_this = pd.DataFrame({tag:[compound[tag]] for tag in tags})
    if fout is not None:
      df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    n_out+=1
    tq.update(n=1)
  tq.close()
  logging.info(f"IDs: {len(ids)}; n_out: {n_out}")
  return df

#############################################################################
def ListCompounds(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; tq=None; skip=0; nchunk=100;
  n_total = requests.get(f"{base_url}/Compounds/count").json()['count']
  while True:
    if tq is None: tq = tqdm.tqdm(total=n_total, unit="cpds")
    filter_arg = """%7B"skip"%3A"""+str(skip)+"""%2C"limit"%3A"""+str(nchunk)+"""%7D"""
    #url = f"{base_url}/Compounds?filter={urllib.parse.quote(filter_arg)}"
    url = f"{base_url}/Compounds?filter={filter_arg}"
    response = requests.get(url)
    if response.status_code != requests.codes.ok: break
    rval = response.json()
    if not rval: break
    compounds = rval
    for compound in compounds:
      logging.debug(json.dumps(compound, indent=2))
      if not tags:
        tags = list(compound.keys())
        for tag in tags[:]:
          if type(compound[tag]) in (list, dict):
            tags.remove(tag)
            logging.info(f"Ignoring tag \"{tag}\"")
      df_this = pd.DataFrame({tag:[compound[tag]] for tag in tags})
      if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
      tq.update(n=1)
    skip+=nchunk
  tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def SearchDataset(searchTerm, lincs, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  url = base_url+'/PublicDatasets/findTermMeta'
  d = {'term':searchTerm}
  if lincs: d['lincs'] = True
  response = requests.post(url, data=d)
  rval = response.json()
  logging.debug(json.dumps(rval, indent=2))
  dsets = rval['data'] if 'data' in rval else []
  for dset in dsets:
    logging.debug(json.dumps(dset, indent=2))
    if not tags:
      tags = [tag for tag in dset.keys() if type(dset[tag]) not in (list, dict)]
    df_this = pd.DataFrame({tag:[dset[tag]] for tag in tags})
    if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def SearchSignature(ids, lincs, base_url=BASE_URL, fout=None):
  #SignatureMeta?filter={"where":{"lincspertid":"LSM-2121"},"limit":10}
  n_out=0; tags=None; df=None;
  for id_this in ids:
    url = base_url+'/SignatureMeta?filter={"where":{"lincspertid":"'+id_this+'"}}'
    response = requests.get(url)
    rval = response.json()
    logging.debug(json.dumps(rval, indent=2))
    sigs = rval
    for sig in sigs:
      logging.debug(json.dumps(sig, indent=2))
      if not tags:
        tags = [tag for tag in sig.keys() if type(sig[tag]) not in (list, dict)]
      df_this = pd.DataFrame({tag:[sig[tag]] for tag in tags})
      if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"IDs: {len(ids)}; n_sig: {df.shape[0]}")
  return df

#############################################################################
def GetSignature(ids, ngene, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; tq=None;
  url = f"{base_url}/ilincsR/downloadSignature"
  d = {'sigID':(','.join(ids)), 'display':True, 'noOfTopGenes':ngene}
  response = requests.post(url, data=d)
  rval = response.json()
  logging.debug(json.dumps(rval, indent=2))
  genes = rval['data']['signature'] if 'data' in rval and 'signature' in rval['data'] else []
  for gene in genes:
    logging.debug(json.dumps(gene, indent=2))
    if not tags:
      tags = [tag for tag in gene.keys() if type(gene[tag]) not in (list, dict)]
    df_this = pd.concat([df, pd.DataFrame({tag:[gene[tag]] for tag in tags})])
    if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
  logging.info(f"IDs: {len(ids)}; n_out: {n_out}")
  return df

#############################################################################
