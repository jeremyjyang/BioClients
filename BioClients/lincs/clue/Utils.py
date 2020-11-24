#!/usr/bin/env python3
#############################################################################
### CMap Clue API client.
### CMap is the project; Clue is the platform.
### https://clue.io/api
### https://clue.io/connectopedia/query_api_tutorial
### https://clue.io/connectopedia/perturbagen_types_and_controls
### l1000_type: "landmark"|"inferred"|"best inferred"|"not inferred"
### BING = Best inferred plus Landmark
### API services: cells, genes, perts, pcls, plates, profiles, sigs,
### probeset_to_entrez_id, rep_fda_exclusivity
#############################################################################
### Apps:
### https://clue.io/cell-app
### https://clue.io/repurposing-app
#############################################################################
### curl -X GET --header "user_key: YOUR_KEY_HERE" 'https://api.clue.io/api/cells?filter=\{"where":\{"provider_name":"ATCC"\}\}' |python3 -m json.tool
#############################################################################
import sys,os,re,argparse,json,logging
import pandas as pd
import urllib.parse
#
from ...util import rest
#
API_HOST="api.clue.io"
API_BASE_PATH="/api"
BASE_URL='https://'+API_HOST+API_BASE_PATH
N_CHUNK=200
#
#############################################################################
def ListDatatypes(params, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = base_url+'/dataTypes'
  rval = rest.Utils.GetURL(url, headers=headers, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  dts = rval
  for dt in dts:
    if not tags:
      tags = [tag for tag in dt.keys() if type(dt[tag]) not in (list, dict)]
    df = pd.concat([df, pd.DataFrame({tags[j]:[dt[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_datatype: {df.shape[0]}")
  return df

#############################################################################
def ListDatasets(params, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = (base_url+'/datasets')
  rval = rest.Utils.GetURL(url, headers=headers, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  dsets = rval
  for dset in dsets:
    if not tags:
      tags = [tag for tag in dset.keys() if type(dset[tag]) not in (list, dict)]
    df = pd.concat([df, pd.DataFrame({tags[j]:[dset[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_dataset: {df.shape[0]}")
  return df

#############################################################################
def ListPerturbagenClasses(params, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = (base_url+'/pcls')
  pcls = rest.Utils.GetURL(url, headers=headers, parse_json=True)
  for pcl in pcls:
    if not tags: tags = list(pcl.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[pcl[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_pertclasses: {df.shape[0]}")
  return df

#############################################################################
def GetGenes(params, ids, id_type, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  url_base = (base_url+'/genes?user_key='+params['user_key'])
  for id_this in ids:
    logging.debug('ID: '+id_this)
    i_chunk=0;
    while True:
      qry = ('{"where":{"%s":"%s"},"skip":%d,"limit":%d}'%(id_type, urllib.parse.quote(id_this), i_chunk*N_CHUNK, N_CHUNK))
      url = url_base+('&filter={}'.format(urllib.parse.quote(qry)))
      genes = rest.Utils.GetURL(url, parse_json=True)
      if not genes: break
      for gene in genes:
        if not tags: tags = list(gene.keys())
        df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
      i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_gene: {df.shape[0]}")
  return df

#############################################################################
def ListGenes_Landmark(params, base_url=BASE_URL, fout=None):
  return GetGenes(params, ['landmark'], 'l1000_type', base_url, fout)

#############################################################################
def ListGenes(params, base_url=BASE_URL, fout=None):
  return GetGenes(params, ['landmark', 'inferred', 'best inferred', 'not inferred'], 'l1000_type', base_url, fout)

#############################################################################
### pert_type:
###	trt_cp - Compound
###	trt_sh - shRNA for loss of function (LoF) of gene
###	trt_lig - Peptides and other biological agents (e.g. cytokine)
###	trt_sh.cgs - Consensus signature from shRNAs targeting the same gene
#############################################################################
def GetPerturbagens(params, ids, id_type, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/perts')
  fields = ['pert_id', 'pert_iname', 'pert_type', 'pert_vendor', 'pert_url', 'id', 'pubchem_cid', 'entrez_geneId', 'vector_id', 'clone_name', 'oligo_seq', 'description', 'target', 'structure_url', 'moa', 'pcl_membership', 'tas', 'num_sig', 'status']
  for id_this in ids:
    logging.debug('ID: '+id_this)
    i_chunk=0;
    while True:
      qry = ('{"where":{"%s":"%s"},"fields":[%s],"skip":%d,"limit":%d}'%(id_type, urllib.parse.quote(id_this), (','.join(['"%s"'%f for f in fields])), i_chunk*N_CHUNK, N_CHUNK))
      url = url_base+('?filter={}'.format(urllib.parse.quote(qry)))
      perts = rest.Utils.GetURL(url, headers=headers, parse_json=True)
      if not perts: break
      logging.debug(json.dumps(perts, indent=2))
      for pert in perts:
        if not tags: tags = list(pert.keys())
        df = pd.concat([df, pd.DataFrame({tags[j]:[pert[tags[j]]] for j in range(len(tags))})])
      i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_pert: {df.shape[0]}")
  return df

#############################################################################
def ListPerturbagens(params, base_url=BASE_URL, fout=None):
  pert_types = ['trt_cp', 'trt_lig', 'trt_sh', 'trt_sh.cgs', 'trt_oe', 'trt_oe.mut', 'trt_xpr', 'trt_sh.css', 'ctl_vehicle.cns', 'ctl_vehicle', 'ctl_vector', 'ctl_vector.cns', 'ctl_untrt.cns', 'ctl_untrt']
  return GetPerturbagens(params, pert_types, 'pert_type', base_url, fout)

#############################################################################
def ListDrugs(params, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/rep_drugs')
  i_chunk=0;
  while True:
    qry = ('{"skip":%d,"limit":%d}'%(i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter={}'.format(urllib.parse.quote(qry)))
    drugs = rest.Utils.GetURL(url, headers=headers, parse_json=True)
    if not drugs: break
    for drug in drugs:
      if not tags: tags = list(drug.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[drug[tags[j]]] for j in range(len(tags))})])
    i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_drug: {df.shape[0]}")
  return df

#############################################################################
def GetCells(params, ids, id_type, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/cells')
  n_cell=0;
  for id_this in ids:
    logging.debug('ID: '+id_this)
    i_chunk=0;
    while True:
      qry = ('{"where":{"%s":"%s"},"skip":%d,"limit":%d}'%(id_type, urllib.parse.quote(id_this), i_chunk*N_CHUNK, N_CHUNK))
      url = url_base+('?filter={}'.format(urllib.parse.quote(qry)))
      cells = rest.Utils.GetURL(url, headers=headers, parse_json=True)
      if not cells: break
      logging.debug(json.dumps(cells, indent=2))
      for cell in cells:
        if not tags: tags = list(cell.keys())
        df = pd.concat([df, pd.DataFrame({tags[j]:[cell[tags[j]]] for j in range(len(tags))})])
      i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_cell: {df.shape[0]}")
  return df

#############################################################################
def ListCells(params, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/cells')
  i_chunk=0;
  while True:
    qry = ('{"skip":%d,"limit":%d}'%(i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter={}'.format(urllib.parse.quote(qry)))
    cells = rest.Utils.GetURL(url, headers=headers, parse_json=True)
    if not cells: break
    for cell in cells:
      if not tags: tags = list(cell.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[cell[tags[j]]] for j in range(len(tags))})])
    i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_cell: {df.shape[0]}")
  return df

#############################################################################
def CountSignatures(params, args, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = (base_url+'/sigs/count?where='+args.clue_where)
  sigs = rest.Utils.GetURL(url, headers=headers, parse_json=True)
  for sig in sigs:
    if not tags: tags = list(sig.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[sig[tags[j]]] for j in range(len(tags))})])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_sig: {df.shape[0]}")
  return df

#############################################################################
def GetSignatures(params, args, base_url=BASE_URL, fout=None):
  tags=None; df=pd.DataFrame();
  fields = ['pert_id','pert_iname','pert_desc','pert_dose','cell_id','provenance_code','target_seq','target_is_lm','target_is_bing','target_zs','dn100_bing','up100_bing']
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/sigs')
  i_chunk=0;
  while True:
    qry = ('{"where":%s,"fields":[%s],"skip":%d,"limit":%d}'%(args.clue_where, (','.join(['"%s"'%f for f in fields])), args.skip+i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter=%s'%(qry))
    sigs = rest.Utils.GetURL(url, headers=headers, parse_json=True)
    if not sigs: break
    logging.debug(json.dumps(sigs, indent=2))
    for sig in sigs:
      if not tags: tags = list(sig.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[sig[tags[j]]] for j in range(len(tags))})])
    i_chunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"IDs: {len(ids)}")
  logging.info(f"n_sig: {df.shape[0]}")
  return df

#############################################################################
