#!/usr/bin/env python3
"""
Reactome REST API utilities.
https://reactome.org/ContentService/
https://reactome.org/ContentService/data/pathways/top/9606
"""
import sys,os,re,json,time,logging
#
from ..util import rest_utils
#
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Content-type':'text/plain','Accept':OFMTS['JSON']}
#
##############################################################################
def ListToplevelPathways(base_url, fout):
  n_out=0;
  species="9606";
  try:
    rval = rest_utils.GetURL(base_url+'/data/pathways/top/%s'%(species), parse_json=True)
  except Exception as e:
    logging.error('%s'%(e))
  pathways = rval
  tags = None;
  for pathway in pathways:
    if not tags:
      tags = pathway.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [str(pathway[tag]) if tag in pathway else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('Top-level pathways: %d'%n_out)

##############################################################################
def ListDiseases(base_url, fout):
  n_out=0;
  try:
    rval = rest_utils.GetURL(base_url+'/getDiseases')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','displayName','definition','schemaClass']
  fout.write('\t'.join(tags)+'\n')
  for line in rval.splitlines():
    idval, doid = re.split(r'\t', line)
    disease = GetDisease(base_url, idval)
    vals=[]
    for tag in tags:
      vals.append(disease[tag] if tag in disease else '')
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('diseases: %d'%n_out)

##############################################################################
def ListProteins(base_url, fout):
  n_out=0;
  try:
    rval = rest_utils.GetURL(base_url+'/getUniProtRefSeqs')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','species','name','displayName','description','definition','schemaClass']
  fout.write('\t'.join(tags)+'\n')
  for line in rval.splitlines():
    idval, uniprot = re.split(r'\t', line)
    protein = GetProtein(base_url, idval)
    vals=[]
    for tag in tags:
      vals.append(protein[tag] if tag in protein else '')
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('proteins: %d'%n_out)

##############################################################################
def ListCompounds(base_url, fout):
  try:
    from rdkit import Chem
  except Exception as e:
    logging.error("RDKit not installed.")
    return
  n_out=0;
  try:
    rval = rest_utils.GetURL(base_url+'/getReferenceMolecules')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','name','displayName','formula','schemaClass']
  fout.write('\t'.join(tags+['smiles'])+'\n')
  for line in rval.splitlines():
    idval, chebi = re.split(r'\t', line)
    compound = GetCompound(base_url, idval)
    vals=[]
    if (type(compound['name']) is types.ListType):
      compound['name']= compound['name'][0]
    for tag in tags:
      vals.append(compound[tag] if tag in compound else '')
    mdlstr = compound['atomicConnectivity'] if (compound and 'atomicConnectivity' in compound) else ''
    smiles=''
    if mdlstr:
      #logging.info('DEBUG: mdlstr="%s"'%mdlstr)
      mdlstr = re.sub(r'\\n', '\n', mdlstr)
      try:
        mol = Chem.MolFromMolBlock(mdlstr)
        smiles = Chem.MolToSmiles(mol)
      except Exception as e:
        logging.error('RDKit Error: %s'%(e))
    fout.write('\t'.join(vals+[smiles])+'\n')
    n_out+=1
  logging.info('compounds: %d'%n_out)

##############################################################################
def GetDisease(base_url, did, fout):
  GetEntity(base_url, [did], 'Disease', fout)

##############################################################################
def GetProtein(base_url, pid, fout):
  GetEntity(base_url, [pid], 'EntityWithAccessionedSequence', fout)

##############################################################################
def GetCompound(base_url, cid, fout):
  GetEntity(base_url, [cid], 'ReferenceMolecule', fout)

##############################################################################
def GetEntity(base_url, ids, ctype, fout):
  for id_this in ids:
    rval=rest_utils.GetURL(base_url+'/queryById/%s/%s'%(ctype, id_this), parse_json=True)
    fout.write(json.dumps(rval, sort_keys=True, indent=2)+'\n')

##############################################################################
def PathwaysForEntities(base_url, ids, fout):
  n_all=0; n_out=0; n_err=0;
  d=('ID='+(','.join(ids))) ##plain text POST body, e.g. "ID=170075,176374,68557"

  rval=rest_utils.PostURL(base_url+'/pathwaysForEntities', data=d, headers=HEADERS, parse_json=True)
  #fout.write(json.dumps(rval, sort_keys=True, indent=2)+'\n')

  pathways = rval
  tags=[];
  for pathway in pathways:
    n_all+=1
    if n_all==1 or not tags:
      tags=sorted(list(set(pathway.keys()) - set(['species','stableIdentifier'])))
      fout.write(','.join(tags+['stableId','stableIdName'])+'\n')

    vals=[];
    for tag in tags:
      vals.append(pathway[tag] if tag in pathway else '')
    vals.append(pathway['stableIdentifier']['dbId'])
    vals.append(pathway['stableIdentifier']['displayName'])

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all, n_out, n_err))

##############################################################################
def PathwaysForGenes(base_url, ids, fout):
  n_all=0; n_out=0; n_err=0;
  d=(','.join(ids)) ##plain text POST body

  rval=rest_utils.PostURL(base_url+'/queryHitPathways', data=d, headers=HEADERS, parse_json=True)
  #fout.write(json.dumps(rval, sort_keys=True, indent=2)+'\n')

  pathways = rval
  tags=[];
  for pathway in pathways:
    n_all+=1
    if n_all==1 or not tags:
      tags=sorted(list(set(pathway.keys()) - set(['species','stableIdentifier'])))
      fout.write('\t'.join(tags+['stableId','stableIdName'])+'\n')

    vals=[];
    for tag in tags:
      vals.append(pathway[tag] if tag in pathway else '')
    vals.append(pathway['stableIdentifier']['dbId'])
    vals.append(pathway['stableIdentifier']['displayName'])

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all, n_out, n_err))

##############################################################################
def PathwayParticipants(base_url, id_query, fout):
  n_all=0; n_out=0; n_err=0;
  rval = rest_utils.GetURL(base_url+'/pathwayParticipants/%s'%(id_query), parse_json=True)
  fout.write(json.dumps(rval, sort_keys=True, indent=2)+'\n')

  if not (rval and type(rval) is types.ListType):
    return
  parts = rval
  tags=[];
  for part in parts:
    n_all+=1
    if n_all==1 or not tags:
      tags=sorted(list(set(part.keys()) - set(['species','stableIdentifier'])))
      fout.write('\t'.join(tags+['stableId','stableIdName'])+'\n')

    vals=[];
    for tag in tags:
      vals.append(part[tag] if tag in part else '')

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d; n_out: %d; n_err: %d'%(n_all, n_out, n_err))

##############################################################################
