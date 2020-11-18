#!/usr/bin/env python3
"""
Reactome REST API utilities.
https://reactome.org/ContentService/
https://reactome.org/ContentService/data/pathways/top/9606
"""
import sys,os,re,json,time,logging
import pandas as pd
#
from ..util import rest
#
API_HOST='reactome.org'
API_BASE_PATH='/ContentService'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
HEADERS={'Content-type':'text/plain','Accept':OFMTS['JSON']}
#
##############################################################################
def ListToplevelPathways(base_url=BASE_URL, fout=None):
  tags=None; species="9606"; df=pd.DataFrame();
  pathways = rest.Utils.GetURL(base_url+f'/data/pathways/top/{species}', parse_json=True)
  for pathway in pathways:
    if not tags: tags = list(pathway.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] if tags[j] in pathway else '' for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('Top-level pathways: {}'.format(df.shape[0]))

##############################################################################
def GetEntity(idval, ctype, base_url=BASE_URL):
  return rest.Utils.GetURL(base_url+f'/queryById/{ctype}/{idval}', parse_json=True)

##############################################################################
def ListDiseases(base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  rval = rest.Utils.GetURL(base_url+'/data/diseases', parse_json=True)
  diseases = rval
  for disease in diseases:
    if not tags: tags = list(disease.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] if tags[j] in disease else '' for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_diseases: {}'.format(df.shape[0]))
  return df

##############################################################################
def ListProteins(base_url=BASE_URL, fout=None):
  df=pd.DataFrame();
  rval = rest.Utils.GetURL(base_url+'/getUniProtRefSeqs')
  tags=['identifier', 'dbId', 'species', 'name', 'displayName', 'description', 'definition', 'schemaClass']
  for line in rval.splitlines():
    idval, uniprot = re.split(r'\t', line)
    protein = GetEntity(idval, 'EntityWithAccessionedSequence', base_url)
    df = pd.concat([df, pd.DataFrame({tags[j]:[protein[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_proteins: {}'.format(df.shape[0]))
  return df

##############################################################################
def ListCompounds(base_url=BASE_URL, fout=None):
  df=pd.DataFrame();
  try:
    from rdkit import Chem
  except Exception as e:
    logging.error("RDKit not installed.")
    return
  rval = rest.Utils.GetURL(base_url+'/getReferenceMolecules')
  tags = ['identifier', 'dbId', 'name', 'displayName', 'formula', 'schemaClass']
  for line in rval.splitlines():
    idval, chebi = re.split(r'\t', line)
    compound = GetEntity(idval, 'ReferenceMolecule', base_url)
    mdlstr = compound['atomicConnectivity'] if (compound and 'atomicConnectivity' in compound) else ''
    smiles=''
    if mdlstr:
      logging.debug(f'{mdlstr}')
      mdlstr = re.sub(r'\\n', '\n', mdlstr)
      try:
        mol = Chem.MolFromMolBlock(mdlstr)
        smiles = Chem.MolToSmiles(mol)
      except Exception as e:
        logging.error(f'RDKit Error: {e}')
    df = pd.concat([df, pd.DataFrame({tags[j]:[compound[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_compounds: {}'.format(df.shape[0]))
  return df

##############################################################################
def PathwaysForEntities(ids, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  d=('ID='+(','.join(ids))) ##plain text POST body, e.g. "ID=170075,176374,68557"
  rval = rest.Utils.PostURL(base_url+'/pathwaysForEntities', data=d, headers=HEADERS, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  pathways = rval
  for pathway in pathways:
    if not tags: tags = list(set(pathway.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def PathwaysForGenes(ids, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  d=(','.join(ids)) ##plain text POST body
  rval = rest.Utils.PostURL(base_url+'/queryHitPathways', data=d, headers=HEADERS, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  pathways = rval
  for pathway in pathways:
    if not tags: tags = list(set(pathway.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def PathwayParticipants(id_query, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  rval = rest.Utils.GetURL(base_url+'/pathwayParticipants/'+id_query, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  parts = rval
  for part in parts:
    if not tags: tags = list(set(part.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[part[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
