#!/usr/bin/env python3
"""
Utility functions for MaayanLab REST APIs.
Alternately could use harmonizomeapi:
http://amp.pharm.mssm.edu/Harmonizome/static/harmonizomeapi.py

https://amp.pharm.mssm.edu/Harmonizome/api/1.0/gene/NANOG
https://amp.pharm.mssm.edu/Harmonizome/api/1.0/gene/NANOG?showAssociations=true
"""
import sys,os,re,json,logging

from ..util import rest
#
##############################################################################
def GetGene(base_url, ids, fout):
  """Gene symbols expected, e.g. NANOG."""
  n_out=0; tags=None;
  for id_this in ids:
    gene = rest.Utils.GetURL(base_url+'/gene/{0}'.format(id_this), parse_json=True)
    logging.debug(json.dumps(gene, indent=2))
    if not tags:
      tags = list(gene.keys())
      fout.write("\t".join(tags)+"\n")
    vals = [(str(gene[tag]) if tag in gene else "") for tag in tags]
    fout.write("\t".join(vals)+"\n")
    n_out+=1
  logging.info("n_out: %d"%(n_out))

##############################################################################
def GetGeneAssociations(base_url, ids, fout):
  """Gene symbols expected, e.g. NANOG."""
  n_out=0; gene_tags=[]; assn_tags=[];
  for id_this in ids:
    gene = rest.Utils.GetURL(base_url+'/gene/{0}?showAssociations=true'.format(id_this), parse_json=True)
    assns = gene["associations"] if "associations" in gene else []
    if not assns: continue
    if not gene_tags:
      for tag in gene.keys():
        if type(gene[tag]) not in (list,dict): gene_tags.append(tag)
    for assn in assns:
      logging.debug(json.dumps(assn, indent=2))
      if not assn_tags:
        assn_tags = list(assn.keys())
        fout.write("\t".join(gene_tags+assn_tags)+"\n")
      vals = [(str(gene[tag]) if tag in gene else "") for tag in gene_tags]+[(str(assn[tag]) if tag in assn else "") for tag in assn_tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
  logging.info("n_out: %d"%(n_out))

##############################################################################
