#!/usr/bin/env python3
#############################################################################
### http://reactomews.oicr.on.ca:8080/ReactomeRESTfulAPI/ReactomeRESTFulAPI.html
### Note: URLs are case sensitive!
#############################################################################
import sys,os,re,json,time,logging
#
from ..util import rest_utils
#
try:
  from rdkit import Chem
except Exception as e:
  logging.error("RDKit not available.")
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Content-type':'text/plain','Accept':OFMTS['JSON']}
#
##############################################################################
def ListDiseases(base_url, fout):
  n_out=0;
  try:
    rval=rest_utils.GetURL(base_url+'/getDiseases')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','displayName','definition','schemaClass']
  fout.write('\t'.join(tags)+'\n')
  for line in rval.splitlines():
    idval, doid = re.split(r'\t',line)
    disease = GetDisease(base_url,idval)
    vals=[]
    for tag in tags:
      vals.append(disease[tag] if disease.has_key(tag) else '')
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('diseases: %d'%n_out)

##############################################################################
def ListProteins(base_url,fout):
  n_out=0;
  try:
    rval=rest_utils.GetURL(base_url+'/getUniProtRefSeqs')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','species','name','displayName','description','definition','schemaClass']
  fout.write('\t'.join(tags)+'\n')
  for line in rval.splitlines():
    idval, uniprot = re.split(r'\t',line)
    protein = GetProtein(base_url,idval)
    vals=[]
    for tag in tags:
      vals.append(protein[tag] if protein.has_key(tag) else '')
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('proteins: %d'%n_out)

##############################################################################
def ListCompounds(base_url, fout):
  n_out=0;
  try:
    rval=rest_utils.GetURL(base_url+'/getReferenceMolecules')
  except Exception as e:
    logging.error('%s'%(e))
  tags=['identifier','dbId','name','displayName','formula','schemaClass']
  fout.write('\t'.join(tags+['smiles'])+'\n')
  for line in rval.splitlines():
    idval, chebi = re.split(r'\t',line)
    compound = GetCompound(base_url,idval)
    vals=[]
    if (type(compound['name']) is types.ListType):
      compound['name']= compound['name'][0]
    for tag in tags:
      vals.append(compound[tag] if compound.has_key(tag) else '')
    mdlstr = compound['atomicConnectivity'] if (compound and compound.has_key('atomicConnectivity')) else ''
    smiles=''
    if mdlstr:
      #logging.info('DEBUG: mdlstr="%s"'%mdlstr)
      mdlstr = re.sub(r'\\n','\n',mdlstr)
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

  rval=rest_utils.PostURL(base_url+'/pathwaysForEntities',data=d,headers=HEADERS,parse_json=True)
  #fout.write(json.dumps(rval,sort_keys=True,indent=2)+'\n')

  pathways = rval
  tags=[];
  for pathway in pathways:
    n_all+=1
    if n_all==1 or not tags:
      tags=sorted(list(set(pathway.keys()) - set(['species','stableIdentifier'])))
      fout.write(','.join(tags+['stableId','stableIdName'])+'\n')

    vals=[];
    for tag in tags:
      vals.append(csv_utils.ToStringForCSV(pathway[tag]) if pathway.has_key(tag) else '')
    vals.append(csv_utils.ToStringForCSV(pathway['stableIdentifier']['dbId']))
    vals.append(csv_utils.ToStringForCSV(pathway['stableIdentifier']['displayName']))

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d'%n_all)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

##############################################################################
def PathwaysForGenes(base_url,ids,fout):
  n_all=0; n_out=0; n_err=0;
  d=(','.join(ids)) ##plain text POST body

  rval=rest_utils.PostURL(base_url+'/queryHitPathways',data=d,headers=HEADERS,parse_json=True)
  #fout.write(json.dumps(rval,sort_keys=True,indent=2)+'\n')

  pathways = rval
  tags=[];
  for pathway in pathways:
    n_all+=1
    if n_all==1 or not tags:
      tags=sorted(list(set(pathway.keys()) - set(['species','stableIdentifier'])))
      fout.write('\t'.join(tags+['stableId','stableIdName'])+'\n')

    vals=[];
    for tag in tags:
      vals.append(csv_utils.ToStringForCSV(pathway[tag]) if pathway.has_key(tag) else '')
    vals.append(csv_utils.ToStringForCSV(pathway['stableIdentifier']['dbId']))
    vals.append(csv_utils.ToStringForCSV(pathway['stableIdentifier']['displayName']))

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d'%n_all)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

##############################################################################
def PathwayParticipants(base_url,id_query,fout):
  n_all=0; n_out=0; n_err=0;
  rval=rest_utils.GetURL(base_url+'/pathwayParticipants/%s'%(id_query),parse_json=True)
  fout.write(json.dumps(rval,sort_keys=True,indent=2)+'\n')

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
      vals.append(csv_utils.ToStringForCSV(part[tag]) if part.has_key(tag) else '')

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d'%n_all)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

##############################################################################
