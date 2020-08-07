#!/usr/bin/env python3
"""
Utility functions for JensenLab REST APIs.
https://api.jensenlab.org/Textmining?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
https://api.jensenlab.org/Textmining?query=jetlag[tiab]%20OR%20jet-lag[tiab]&type2=9606&limit=10&format=json
https://api.jensenlab.org/Knowledge?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
https://api.jensenlab.org/Experiments?type1=-26&id1=DOID:10652&type2=9606&limit=10&format=json
"""
import sys,os,re,json,time,logging

from ..util import rest_utils
#
##############################################################################
def GetDiseaseGenes(base_url, channel, ids, nmax, fout):
  n_out=0; tags=None;
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/{CHANNEL}?type1=-26&id1={DOID}&type2=9606&limit={NMAX}&format=json'.format(CHANNEL=channel, DOID=id_this, NMAX=nmax), parse_json=True)
    genes = rval[0] #dict
    ensgs = list(genes.keys())
    flag = rval[1] #?
    for ensg in ensgs:
      gene = genes[ensg]
      logging.debug(json.dumps(gene, indent=2))
      if not tags:
        tags = list(gene.keys())
        fout.write("queryId\t"+("\t".join(tags))+"\n")
      vals = [(str(gene[tag]) if tag in gene else "") for tag in tags]
      fout.write(str(id_this)+"\t"+("\t".join(vals))+"\n")
      n_out+=1
  logging.info("n_out: %d"%(n_out))

##############################################################################
def GetPubmedComentionGenes(base_url, ids, fout):
  """Search by co-mentioned terms."""
  n_out=0; tags=None;
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/Textmining?query={0}[tiab]&type2=9606&limit=10&format=json'.format(id_this), parse_json=True)
    genes = rval[0] #dict
    ensgs = list(genes.keys())
    flag = rval[1] #?
    for ensg in ensgs:
      gene = genes[ensg]
      logging.debug(json.dumps(gene, indent=2))
      if not tags:
        tags = list(gene.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [(str(gene[tag]) if tag in gene else "") for tag in tags]
      fout.write("\t".join(vals)+"\n")
  logging.info("n_out: %d"%(n_out))

##############################################################################
