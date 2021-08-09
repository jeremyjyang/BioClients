#!/usr/bin/env python3
"""
LINCS REST API client
New (2019) iLINCS: 
http://www.ilincs.org/ilincs/APIinfo
http://www.ilincs.org/ilincs/APIdocumentation
(http://lincsportal.ccs.miami.edu/dcic/api/ DEPRECATED?)
"""
###
import sys,os,re,json,logging
import urllib,urllib.parse
import pandas as pd
#
from ..util import rest
#
API_HOST="www.ilincs.org"
API_BASE_PATH="/api"
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
#############################################################################
def GetGene(ids, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  for id_this in ids:
    url = base_url+'/GeneInfos/'+id_this
    rval = rest.Utils.GetURL(url, parse_json=True)
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
  tags=None; df=pd.DataFrame();
  for id_this in ids:
    url = base_url+'/PublicDatasets/'+id_this
    rval = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
    dset = rval
    df = pd.concat([df, pd.DataFrame({tags[j]:[dset[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  return df

#############################################################################
def GetCompound(ids, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  for id_this in ids:
    url = base_url+'/Compounds/%s'%id_this
    rval = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
    cpd = rval
    df = pd.concat([df, pd.DataFrame({tags[j]:[cpd[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}; n_cpd: {df.shape[0]}")
  return df

#############################################################################
def ListCompounds(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  skip=0; nchunk=100;
  while True:
    filter_arg = """%7B"skip"%3A"""+str(skip)+"""%2C"limit"%3A"""+str(nchunk)+"""%7D"""
    #url = f"{base_url}/Compounds?filter={urllib.parse.quote(filter_arg)}"
    url = f"{base_url}/Compounds?filter={filter_arg}"
    rval = rest.Utils.GetURL(url, parse_json=True)
    if not rval: break
    compounds = rval
    for compound in compounds:
      logging.debug(json.dumps(compound, indent=2))
      if not tags:
        tags = [tag for tag in compound.keys() if type(compound[tag]) not in (list, dict)]
      df_this = pd.DataFrame({tags[j]:[compound[tags[j]]] for j in range(len(tags))})
      if fout is None:
        df = pd.concat([df, df_this])
      else:
        df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    skip += nchunk
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def SearchDataset(searchTerm, lincs, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  url = base_url+'/PublicDatasets/findTermMeta'
  d = {'term':searchTerm}
  if lincs: d['lincs'] = True
  rval = rest.Utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  dsets = rval['data'] if 'data' in rval else []
  for dset in dsets:
    logging.debug(json.dumps(dset, indent=2))
    if not tags:
      tags = [tag for tag in dset.keys() if type(dset[tag]) not in (list, dict)]
    df = pd.concat([df, pd.DataFrame({tags[j]:[dset[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"Datasets: {df.shape[0]}")
  return df

#############################################################################
def SearchSignature(ids, lincs, base_url=BASE_URL, fout=None):
  #SignatureMeta?filter={"where":{"lincspertid":"LSM-2121"},"limit":10}
  tags=None; df=pd.DataFrame();
  for id_this in ids:
    url = base_url+'/SignatureMeta?filter={"where":{"lincspertid":"'+id_this+'"}}'
    rval = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    sigs = rval
    for sig in sigs:
      logging.debug(json.dumps(sig, indent=2))
      if not tags:
        tags = [tag for tag in sig.keys() if type(sig[tag]) not in (list, dict)]
      df = pd.concat([df, pd.DataFrame({tags[j]:[sig[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}; n_sig: {df.shape[0]}")
  return df

#############################################################################
def GetSignature(ids, ngene, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  url = base_url+'/ilincsR/downloadSignature'
  d = {'sigID':(','.join(ids)), 'display':True, 'noOfTopGenes':ngene}
  rval = rest.Utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  genes = rval['data']['signature'] if 'data' in rval and 'signature' in rval['data'] else []
  for gene in genes:
    logging.debug(json.dumps(gene, indent=2))
    if not tags:
      tags = [tag for tag in gene.keys() if type(gene[tag]) not in (list, dict)]
    df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}; n_gene: {df.shape[0]}")
  return df

#############################################################################
