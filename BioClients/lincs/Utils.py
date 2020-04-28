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
#
from ..util import rest_utils
#
#############################################################################
def GetGene(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/GeneInfos/%s'%id_this
    rval = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def GetDataset(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/PublicDatasets/%s'%id_this
    rval = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def GetCompound(base_url, ids, fout):
  tags=None; n_cpd=0;
  for id_this in ids:
    url = base_url+'/Compounds/%s'%id_this
    cpd = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(cpd, indent=2))
    if not tags:
      tags = [tag for tag in cpd.keys() if type(cpd[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(cpd[tag]) if tag in cpd else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_cpd+=1
  logging.info("IDs: {0}; n_cpd: {1}".format(len(ids), n_cpd))

#############################################################################
def SearchDataset(base_url, searchTerm, lincs, fout):
  tags=None;
  url = base_url+'/PublicDatasets/findTermMeta'
  d = {'term':searchTerm}
  if lincs: d['lincs'] = True
  rval = rest_utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  dsets = rval['data'] if 'data' in rval else []
  for dset in dsets:
    logging.debug(json.dumps(dset, indent=2))
    if not tags:
      tags = [tag for tag in dset.keys() if type(dset[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(dset[tag]) if tag in dset else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("Datasets: {0}".format(len(dsets)))

#############################################################################
def SearchSignature(base_url, ids, lincs, fout):
  #SignatureMeta?filter={"where":{"lincspertid":"LSM-2121"},"limit":10}
  tags=None; n_sig=0;
  for id_this in ids:
    url = base_url+'/SignatureMeta?filter={"where":{"lincspertid":"%s"}}'%id_this
    sigs = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(sigs, indent=2))
    for sig in sigs:
      logging.debug(json.dumps(sig, indent=2))
      if not tags:
        tags = [tag for tag in sig.keys() if type(sig[tag]) not in (list, dict)]
        fout.write('\t'.join(tags)+'\n')
      vals = [str(sig[tag]) if tag in sig else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_sig+=1
  logging.info("IDs: {0}; n_sig: {1}".format(len(ids), n_sig))

#############################################################################
def GetSignature(base_url, ids, ngene, fout):
  tags=None; n_gene=0;
  url = base_url+'/ilincsR/downloadSignature'
  d = {'sigID':(','.join(ids)), 'display':True, 'noOfTopGenes':ngene}
  rval = rest_utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  genes = rval['data']['signature'] if 'data' in rval and 'signature' in rval['data'] else []
  for gene in genes:
    logging.debug(json.dumps(gene, indent=2))
    if not tags:
      tags = [tag for tag in gene.keys() if type(gene[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(gene[tag]) if tag in gene else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_gene+=1
  logging.info("IDs: {0}; n_gene: {1}".format(len(ids), n_gene))

#############################################################################
