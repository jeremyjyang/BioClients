#!/usr/bin/env python3
"""
Utilities for the AMP T2D REST API.
http://www.type2diabetesgenetics.org/
http://www.kp4cd.org/apis/t2d
http://52.54.103.84/kpn-kb-openapi/

DEPICT software (Pers, TH, et al., 2015)
"""
###
import sys,os,re,json,time,logging
#
from ...util import rest
#
#############################################################################
def ListTissues(base_url, fout):
  rval = rest.Utils.GetURL(base_url+'/graph/tissue/list/object', parse_json=True)
  tissues = rval["data"] if "data" in rval else []
  tags = None; n_out=0;
  for tissue in tissues:
    logging.debug(json.dumps(tissue, indent=2))
    if not tags:
      tags = tissue.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [str(tissue[tag]) if tag in tissue else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out += 1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def ListPhenotypes(base_url, fout):
  rval=rest.Utils.GetURL(base_url+'/graph/phenotype/list/object', parse_json=True)
  phenotypes = rval["data"] if "data" in rval else []
  tags = None; n_out=0;
  for phenotype in phenotypes:
    logging.debug(json.dumps(phenotype, indent=2))
    if not tags:
      tags = phenotype.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [str(phenotype[tag]) if tag in phenotype else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out += 1
  logging.info("n_out: %d"%(n_out))

##############################################################################
def DepictGenePathway(base_url, gene, phenotype, max_pval, fout):
  url = base_url+('/testcalls/depict/genepathway/object?gene=%s&phenotype=%s&lt_value=%f'%(gene, phenotype, max_pval))
  rval = rest.Utils.GetURL(url, parse_json=True)
  pathways = rval["data"] if "data" in rval else []
  tags = None; n_out=0;
  for pathway in pathways:
    logging.debug(json.dumps(pathway, indent=2))
    if not tags:
      tags = pathway.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [str(pathway[tag]) if tag in pathway else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out += 1
  logging.info("n_out: %d"%(n_out))

##############################################################################
