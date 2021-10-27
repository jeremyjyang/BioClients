#!/usr/bin/env python3
"""
Utility functions for JensenLab REST APIs.
https://api.jensenlab.org/Textmining?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
https://api.jensenlab.org/Textmining?query=jetlag[tiab]%20OR%20jet-lag[tiab]&type2=9606&limit=10&format=json
https://api.jensenlab.org/Knowledge?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
https://api.jensenlab.org/Experiments?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
"""
import sys,os,re,json,time,logging
import pandas as pd

from ..util import rest
#
API_HOST='api.jensenlab.org'
API_BASE_PATH=''
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def GetDiseaseGenes(channel, ids, nmax, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    rval = rest.GetURL(base_url+f'/{channel}?type1=-26&id1={id_this}&type2=9606&limit={nmax}&format=json', parse_json=True)
    genes = rval[0] #dict
    ensgs = list(genes.keys())
    flag = rval[1] #?
    for ensg in ensgs:
      gene = genes[ensg]
      logging.debug(json.dumps(gene, indent=2))
      if not tags: tags = list(gene.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(df.shape[0]))
  return df

##############################################################################
def GetPubmedComentionGenes(ids, base_url=BASE_URL, fout=None):
  """Search by co-mentioned terms."""
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    rval = rest.GetURL(base_url+f'/Textmining?query={id_this}[tiab]&type2=9606&limit=10&format=json', parse_json=True)
    genes = rval[0] #dict
    ensgs = list(genes.keys())
    flag = rval[1] #?
    for ensg in ensgs:
      gene = genes[ensg]
      logging.debug(json.dumps(gene, indent=2))
      if not tags: tags = list(gene.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(df.shape[0]))
  return df

##############################################################################
