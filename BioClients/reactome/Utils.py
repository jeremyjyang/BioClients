#!/usr/bin/env python3
"""
Reactome REST API utilities.
https://reactome.org/ContentService/
https://reactome.org/ContentService/data/pathways/top/9606

https://reactome.org/documentation/data-model

"Life on the cellular level is a network of molecular interactions. Molecules are synthesized and degraded, undergo a bewildering array of temporary and permanent modifications, are transported from one location to another, and form complexes with other molecules. Reactome represents all of this complexity as reactions in which input physical entities are converted to output entities."

"PhysicalEntities include individual molecules, multi-molecular complexes, and sets of molecules or complexes grouped together on the basis of shared characteristics. Molecules are further classified as genome encoded (DNA, RNA, and proteins) or not (all others). Attributes of a PhysicalEntity instance capture the chemical structure of an entity, including any covalent modifications in the case of a macromolecule, and its subcellular localization."
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
HEADERS={'Content-type':'text/plain', 'Accept':'application/json'}
#
##############################################################################
def DBInfo(base_url=BASE_URL, fout=None):
  name = rest.GetURL(base_url+'/data/database/name')
  version = rest.GetURL(base_url+'/data/database/version')
  df = pd.DataFrame({'param':['name', 'version'], 'value':[name, version]});
  if fout: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
def ListToplevelPathways(base_url=BASE_URL, fout=None):
  tags=None; species="9606"; df=pd.DataFrame();
  pathways = rest.GetURL(base_url+f'/data/pathways/top/{species}', parse_json=True)
  for pathway in pathways:
    if not tags: tags = list(pathway.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] if tags[j] in pathway else [''] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('Top-level pathways: {}'.format(df.shape[0]))
  return df

##############################################################################
def ListDiseases(base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  rval = rest.GetURL(base_url+'/data/diseases', parse_json=True)
  diseases = rval
  for disease in diseases:
    if not tags: tags = list(disease.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] if tags[j] in disease else [''] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_diseases: {}'.format(df.shape[0]))
  return df

##############################################################################
def QueryEntry(ids, base_url=BASE_URL, fout=None):
  """Stable or database IDs required, such as for disease, or pathway."""
  tags=None; df=pd.DataFrame(); classNames=set();
  for id_this in ids:
    rval = rest.GetURL(base_url+f'/data/query/{id_this}', parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
    ent = rval
    if not tags: tags = list(ent.keys())
    if 'className' in ent: classNames.add(ent['className'])
    df = pd.concat([df, pd.DataFrame({tags[j]:[ent[tags[j]]] if tags[j] in ent else [''] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_out {}: {}'.format((list(classNames)), df.shape[0]))
  return df

##############################################################################
def GetInteractors(ids, base_url=BASE_URL, fout=None):
  """IDs may be UniProt accessions."""
  tags=None; df=pd.DataFrame(); classNames=set();
  for id_this in ids:
    rval = rest.GetURL(base_url+f'/interactors/static/molecule/{id_this}/details', parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
    ents = rval["entities"] if "entities" in rval else []
    for ent in ents:
      intrs = ent["interactors"] if "interactors" in ents else []
      for intr in intrs:
        if not tags: tags = list(intr.keys())
        if 'className' in intr: classNames.add(intr['className'])
        df = pd.concat([df, pd.DataFrame({tags[j]:[intr[tags[j]]] if tags[j] in intr else [''] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_out {}: {}'.format((list(classNames)), df.shape[0]))
  return df

##############################################################################
def ListCompounds(base_url=BASE_URL, fout=None):
  """NOT WORKING."""
  tags=[]; df=pd.DataFrame();
  rval = rest.GetURL(base_url+'/getReferenceMolecules', parse_json=True)
  mols = rval
  for mol in mols:
    if not tags: tags = list(mol.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[mol[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_mols: {}'.format(df.shape[0]))
  return df

##############################################################################
def GetPathwaysForEntities(ids, base_url=BASE_URL, fout=None):
  """NOT WORKING."""
  tags=[]; df=pd.DataFrame();
  d=('ID='+(','.join(ids))) ##plain text POST body, e.g. "ID=170075,176374,68557"
  rval = rest.PostURL(base_url+'/pathwaysForEntities', data=d, headers=HEADERS, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  pathways = rval
  for pathway in pathways:
    if not tags: tags = list(set(pathway.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetPathwaysForGenes(ids, base_url=BASE_URL, fout=None):
  """NOT WORKING."""
  tags=[]; df=pd.DataFrame();
  d=(','.join(ids)) ##plain text POST body
  rval = rest.PostURL(base_url+'/queryHitPathways', data=d, headers=HEADERS, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  pathways = rval
  for pathway in pathways:
    if not tags: tags = list(set(pathway.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[pathway[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
def GetPathwayParticipants(id_query, base_url=BASE_URL, fout=None):
  """NOT WORKING."""
  tags=[]; df=pd.DataFrame();
  rval = rest.GetURL(base_url+'/pathwayParticipants/'+id_query, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2)+'\n')
  parts = rval
  for part in parts:
    if not tags: tags = list(set(part.keys()))
    df = pd.concat([df, pd.DataFrame({tags[j]:[part[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info('n_in: {}; n_out: {}'.format(len(ids), df.shape[0]))
  return df

##############################################################################
