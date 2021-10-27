#!/usr/bin/env python3
#############################################################################
### BindingDb Utilities
### http://www.bindingdb.org/bind/BindingDBRESTfulAPI.jsp
### http://www.bindingdb.org/axis2/services/BDBService/getLigandsByUniprots?uniprot=P35355,Q8HZR1&cutoff=1000&code=0&response=application/json
#############################################################################
import sys,os,re,time,json,logging
import urllib.parse

from ..util import rest
#
##############################################################################
def GetLigandsByUniprot(base_url, ids, ic50_max, fout):
  n_out=0; tags=None;
  for id_this in ids:
    rval = rest.GetURL(base_url+'/getLigandsByUniprots?uniprot=%s&cutoff=%d&response=application/json'%(id_this, ic50_max), parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    ligands = rval["getLigandsByUniprotsResponse"]["affinities"] if "getLigandsByUniprotsResponse" in rval and "affinities" in rval["getLigandsByUniprotsResponse"] else []
    for ligand in ligands:
      if not tags:
        tags = ligand.keys()
        fout.write("\t".join(tags)+"\n")
      vals = [(str(ligand[tag]) if tag in ligand else '') for tag in tags]
      fout.write("\t".join(vals)+"\n")
  logging.info("n_out: {}".format(n_out))

##############################################################################
def GetTargetsByCompound(base_url, smiles, sim_min, fout):
  rval = rest.GetURL(base_url+'/getTargetByCompound?smiles=%s&cutoff=%.2f'%(urllib.parse.quote(smiles),
sim_min), parse_xml=True)
  fout.write(rval.tostring())

##############################################################################
