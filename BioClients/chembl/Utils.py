#!/usr/bin/env python3
"""
Utility functions for ChEMBL REST API.
See: https://www.ebi.ac.uk/chembldb/index.php/ws
"""
###
import sys,os,re,json,logging
#
from ..util import rest_utils
#
NCHUNK=100
#
##############################################################################
# {
#   "api_version": "2.6.14", 
#   "chembl_db_version": "ChEMBL_22", 
#   "status": "UP"
# }
##############################################################################
def Status(base_url):
  rval=rest_utils.GetURL(base_url+'/status.json',parse_json=True)
  db_ver = rval['chembl_db_version'] if 'chembl_db_version' in rval else ''
  api_ver = rval['api_version'] if 'api_version' in rval else ''
  status = rval['status'] if 'status' in rval else ''
  logging.debug(json.dumps(rval,sort_keys=True,indent=2))
  return api_ver, db_ver, status

#############################################################################
def GetTargetsByUniprot(uniprot,base_url):
  rval=rest_utils.GetURL(base_url+'/target.json?target_components__accession=%s'%uniprot,parse_json=True)
  tgts=rval['targets'] if (rval and 'targets' in rval) else []
  return tgts

#############################################################################
def Uniprot2ID(uniprot,base_url):
  id_chembl=None
  targets=GetTargetsByUniprot(uniprot,base_url)
  ids = set([])
  for target in targets:
    id_chembl=target['target_chembl_id']
    ids.add(id_chembl)
  if len(ids)>1:
    logging.info('Uniprot ambiguous.')
  for id_chembl in list(ids):
    logging.info('Uniprot: %s -> ChEMBL: %s'%(uniprot,id_chembl))
  return list(ids)

#############################################################################
def GetByID(id_query,base_url,resource):
  rval=None
  try:
    rval=rest_utils.GetURL(base_url+'/'+resource+'/%s.json'%id_query,{},parse_json=True)
  except Exception as e:
    logging.info('HTTP Error (%s): %s'%(res,e))
  return rval

#############################################################################
def GetActivity(ids, resource, api_host, api_base_path, pmin, fout):
  '''Get activity data and necessary references only, due to size concerns.  resource =
assay|target|molecule.  Filter on pChEMBL value, standardized negative log molar half-max response activity.'''
  n_qry=0; n_act=0; n_out=0; n_err=0; tags=None;
  n_pval=0;
  n_pval_ok=0;
  for id_this in ids:
    n_qry+=1
    url_next=(api_base_path+'/activity.json?%s_chembl_id=%s&limit=%d'%(resource,id_this,NCHUNK))
    while True:
      rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
      logging.debug(json.dumps(rval,sort_keys=True,indent=2))
      if type(rval) is not dict:
        n_err+=1
        continue
      acts=rval['activities'] if 'activities' in rval else []
      for act in acts:
        n_act+=1
        if n_act==1 or not tags:
          tags = sorted(act.keys())
          fout.write('\t'.join(tags)+'\n')
        vals=[str(act[tag]) if tag in act else '' for tag in tags]
        if pmin is not None:
          try:
            pval = float(act['pchembl_value'])
            n_pval+=1
            if pval >= pmin:
              n_pval_ok+=1
              fout.write('\t'.join(vals)+'\n')
              n_out+=1
              logging.debug('[%d] pVal ok (%4.1f >= %4.1f)'%(n_act,pval,pmin))
            else:
              logging.debug('[%d] pVal low (%4.1f < %4.1f)'%(n_act,pval,pmin))
          except:
            logging.debug('[%d] pVal missing.'%n_act)
        else:
          fout.write('\t'.join(vals)+'\n')
          n_out+=1
      meta = rval['page_meta'] if 'page_meta' in rval else {}
      url_next = meta['next'] if 'next' in meta else None
      total_count = meta['total_count'] if 'total_count' in meta else None
      if n_act%1000==0:
        logging.info('n_act: %6d / %s'%(n_act,str(total_count) if total_count else '?'))
      if not url_next: break
  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_act: %d'%(n_act))
  if pmin is not None:
    logging.info('n_pval: %d'%(n_pval))
    logging.info('n_pval_ok: %d'%(n_pval_ok))
    logging.info('pVals missing: %d'%(n_act-n_pval))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))

#############################################################################
def ListTargets(api_host, api_base_path, skip, nmax, fout):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; n_err=0; tags=None;
  url_next=(api_base_path+'/target.json?limit=%d'%NCHUNK)
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    tgts=rval['targets'] if rval and 'targets' in rval else []
    for tgt in tgts:
      logging.debug(json.dumps(tgt, indent=2))
      n_tgt+=1
      if n_tgt==1 or not tags:
        tags = sorted(tgt.keys())
        for tag in tags:
          if type(tgt[tag]) in (dict, list, tuple):
            tags.remove(tag)
        tags.extend(['component_count','accession'])
        fout.write('\t'.join(tags)+'\n')
      vals=[str(tgt[tag]) if tag in tgt else '' for tag in tags]
      if 'target_components' in tgt and tgt['target_components']:
        cmts=tgt['target_components']
        n_cmt_this=len(cmts)
        n_cmt+=n_cmt_this
        vals.append('%d'%n_cmt_this)
        vals.append(cmts[0]['accession'] if n_cmt_this==1 else '')
      else:
        logging.debug('no-component target: %s'%vals[0])
        vals.extend(['',''])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    meta = rval['page_meta'] if rval and 'page_meta' in rval else {}
    total_count = meta['total_count'] if 'total_count' in meta else None
    url_next = meta['next'] if 'next' in meta else None
    if n_tgt%1000==0:
      logging.info('%d targets / %s total'%(n_tgt, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_targets: %d'%n_tgt)
  logging.info('n_target_components: %d'%n_cmt)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def GetTarget(tids, base_url, fout):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_qry=0; n_tgt=0; n_cmt=0; n_out=0; n_err=0; tags=None;
  for tid in tids:
    n_qry+=1
    tgt=None
    try:
      tgt=GetByID(tid,base_url,'target')
    except Exception as e:
      logging.info('HTTP Error: %s'%(e))
    if tgt and type(tgt) == dict:
      n_tgt+=1
      if n_tgt==1 or not tags:
        tags = sorted(tgt.keys())
        for tag in tags:
          if type(tgt[tag]) in (dict, list, tuple):
            tags.remove(tag)
        tags.extend(['component_count','accession'])
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(tgt,sort_keys=True,indent=2))
      vals=[str(tgt[tag]) if tag in tgt else '' for tag in tags]
      if 'target_components' in tgt and tgt['target_components']:
        cmts=tgt['target_components']
        n_cmt_this=len(cmts)
        n_cmt+=n_cmt_this
        vals.append('%d'%n_cmt_this)
        vals.append(str(cmts[0]['accession']) if n_cmt_this==1 else '')
      else:
        logging.debug('no-component target: %s'%vals[0])
        vals.extend(['',''])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
  logging.info('n_qry: %d'%n_qry)
  logging.info('n_targets: %d'%n_tgt)
  logging.info('n_target_components: %d'%n_cmt)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def GetDocument(dids, base_url, fout):
  n_qry=0; n_doc=0; n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None;
  for did in dids:
    n_qry+=1
    doc=None
    try:
      doc=GetByID(did, base_url, 'document')
    except Exception as e:
      logging.info('HTTP Error: %s'%(e))
    if doc and type(doc)==dict:
      n_doc+=1
      if n_doc==1 or not tags:
        tags = sorted(doc.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(doc,sort_keys=True,indent=2))
      if 'pubmed_id' in tags and doc[tag]: n_pmid+=1
      if 'doi' in tags and doc[tag]: n_doi+=1
      vals=[str(doc[tag]) if tag in doc else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
  logging.info('n_qry: %d'%n_qry)
  logging.info('n_docs: %d'%n_doc)
  logging.info('n_pmid: %d'%n_pmid)
  logging.info('n_doi: %d'%n_doi)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListSources(api_host, api_base_path,fout):
  n_src=0; n_out=0; n_err=0; tags=None; source_map={};
  url_next=(api_base_path+'/source.json')
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next,parse_json=True)
    if not rval:
      n_err+=1
      continue ## ERROR
    sources=rval['sources']
    for source in sources:
      n_src+=1
      if n_src==1 or not tags:
        tags = sorted(source.keys())
        fout.write('\t'.join(tags)+'\n')
      source_map[source['src_id']] = source
    meta=rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    if not url_next: break
  for src_id in sorted(source_map.keys()):
    source = source_map[src_id]
    vals=[str(source[tag]) if tag in source else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_source: %d'%n_src)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListCellLines(api_host, api_base_path, fout):
  n_cell=0; n_clo=0; n_efo=0; n_out=0; n_err=0; tags=None;
  url_next=(api_base_path+'/cell_line.json')
  rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  if not rval or type(rval) != dict:
    n_err+=1
    logging.info('ERROR: %s'%str(rval))
    return
  cells=rval['cell_lines'] if 'cell_lines' in rval else []
  for cell in cells:
    n_cell+=1
    if n_cell==1 or not tags:
      tags = sorted(cell.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(cell, sort_keys=True, indent=2))
    if 'clo_id' in cell and cell['clo_id']: n_clo+=1
    if 'efo_id' in cell and cell['efo_id']: n_efo+=1
    vals=[str(cell[tag]) if tag in cell else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_cell: %d'%n_cell)
  logging.info('n_clo: %d'%n_clo)
  logging.info('n_efo: %d'%n_efo)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListTissues(api_host, api_base_path, fout):
  n_tissue=0; n_bto=0; n_efo=0; n_caloha=0; n_uberon=0; tags=None;
  n_out=0; n_err=0;
  url_next=(api_base_path+'/tissue.json')
  rval=rest_utils.GetURL('https://'+api_host+url_next,parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  if not rval or type(rval) != dict:
    n_err+=1
    logging.error('%s'%str(rval))
    return
  tissues=rval['tissues'] if 'tissues' in rval else []
  for tissue in tissues:
    n_tissue+=1
    if n_tissue==1 or not tags:
      tags = sorted(tissue.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(tissue, sort_keys=True, indent=2))
    if 'bto_id' in tissue and tissue['bto_id']: n_bto+=1
    if 'efo_id' in tissue and tissue['efo_id']: n_efo+=1
    if 'uberon_id' in tissue and tissue['uberon_id']: n_uberon+=1
    if 'caloha_id' in tissue and tissue['caloha_id']: n_caloha+=1
    vals=[str(tissue[tag]) if tag in tissue else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_tissue: %d'%n_tissue)
  logging.info('n_bto: %d'%n_bto)
  logging.info('n_efo: %d'%n_efo)
  logging.info('n_caloha: %d'%n_caloha)
  logging.info('n_uberon: %d'%n_uberon)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListMechanisms(api_host, api_base_path, fout):
  n_mechanism=0; tags=None;
  n_out=0; n_err=0;
  url_next=(api_base_path+'/mechanism.json')
  rval=rest_utils.GetURL('https://'+api_host+url_next,parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  if not rval or type(rval) != dict:
    n_err+=1
    logging.error('%s'%str(rval))
    return
  mechanisms=rval['mechanisms'] if 'mechanisms' in rval else []
  for mechanism in mechanisms:
    n_mechanism+=1
    if n_mechanism==1 or not tags:
      tags = sorted(mechanism.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(mechanism, sort_keys=True, indent=2))
    vals=[str(mechanism[tag]) if tag in mechanism else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_mechanism: %d'%n_mechanism)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListDocuments(api_host, api_base_path, skip, nmax, fout):
  n_doc=0; n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None;
  url_next=(api_base_path+'/document.json?limit=%d'%NCHUNK)
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval or type(rval) != dict:
      n_err+=1
      logging.error('"%s"'%str(rval))
      break
    docs=rval['documents'] if 'documents' in rval else []
    for doc in docs:
      n_doc+=1
      if n_doc==1 or not tags:
        tags = sorted(doc.keys())
        if 'abstract' in tags: tags.remove('abstract') #unnecessary, verbose
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(doc, sort_keys=True, indent=2))
      if 'pubmed_id' in tags and doc[tag]: n_pmid+=1
      if 'doi' in tags and doc[tag]: n_doi+=1
      vals=[str(doc[tag]) if tag in doc else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_doc%1000==0:
      logging.info('%d docs / %s total'%(n_doc,str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_doc: %d'%n_doc)
  logging.info('n_pmid: %d'%n_pmid)
  logging.info('n_doi: %d'%n_doi)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def ListAssays(api_host, api_base_path, skip, nmax, fout):
  n_ass=0; n_out=0; n_err=0; tags=None;
  url_next=(api_base_path+'/assay.json?offset=%d&limit=%d'%(skip, NCHUNK))
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval or type(rval) != dict:
      logging.error('"%s"'%str(rval))
      n_err+=1
      break ## ERROR
    assays=rval['assays']
    for assay in assays:
      n_ass+=1
      if n_ass==1 or not tags:
        tags = sorted(assay.keys())
        fout.write('\t'.join(tags)+'\n')
      vals=[]
      for tag in tags:
        vals.append(str(assay[tag]) if tag in assay else '')
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    total_count = meta['total_count'] if 'total_count' in meta else None
    url_next = meta['next'] if 'next' in meta else None
    if n_ass%1000==0:
      logging.info('%d assays / %s total'%(n_ass, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_assay: %d'%n_ass)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)
  return

#############################################################################
def SearchAssays(api_host, api_base_path, asrc, atype, skip, nmax, fout):
  '''Select assays based on source and optionally type.'''
  tags=None; n_ass=0; n_out=0; n_err=0;
  url_next=(api_base_path+'/assay.json'+'?offset=%d&limit=%d'%(skip, NCHUNK))
  if asrc:
    url_next+=('&src_id=%d'%(asrc))
  if atype:
    url_next+=('&assay_type=%s'%(atype))
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval or type(rval) != dict:
      logging.error('"%s"'%str(rval))
      n_err+=1
      break ## ERROR
    assays = rval['assays']
    for assay in assays:
      n_ass+=1
      if n_ass==1 or not tags:
        tags = sorted(assay.keys())
        fout.write('\t'.join(tags)+'\n')
      vals=[]
      for tag in tags:
        vals.append(str(assay[tag]) if tag in assay else '')
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_ass%1000==0:
      logging.info('%d assays / %s total'%(n_ass, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_assay: %d'%n_ass)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def GetAssay(base_url, aids, fout):
  tags=None;
  n_ass=0; n_out=0; n_err=0;
  for aid in aids:
    n_ass+=1
    assay=GetByID(aid,base_url,'assay')
    if not assay:
      n_err+=1
      continue
    if n_ass==1 or not tags:
      tags = sorted(assay.keys())
      fout.write('\t'.join(tags)+'\n')
    vals=[]
    for tag in tags:
      vals.append(str(assay[tag]) if tag in assay else '')
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_assay: %d'%n_ass)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

##############################################################################
def GetMolecule(base_url, mids,fout):
  '''Ignore molecule_synonyms.'''
  n_qry=0; n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None;
  for mid in mids:
    n_qry+=1
    mol=None
    try:
      mol=GetByID(mid,base_url,'molecule')
    except Exception as e:
      logging.info('HTTP Error: %s'%(e))
    if mol and type(mol) != dict:
      n_err+=1
      continue
    n_mol+=1
    if n_mol==1:
      tags = sorted(mol.keys())
      for tag in tags[:]:
        if type(mol[tag]) in (dict, list, tuple):
          tags.remove(tag)
      struct_tags = sorted(mol['molecule_structures'].keys())
      prop_tags = sorted(mol['molecule_properties'].keys())
      fout.write('\t'.join(tags+struct_tags+prop_tags+['parent_chembl_id'])+'\n')
    logging.debug(json.dumps(mol,sort_keys=True,indent=2))
    vals=[]
    if 'molecule_hierarchy' in mol and type(mol['molecule_hierarchy'])==dict:
      mol_hier = mol['molecule_hierarchy']
      vals.append(str(mol_hier['parent_chembl_id']) if 'parent_chembl_id' in mol_hier else '')
    for tag in tags:
      vals.append(str(mol[tag]) if tag in mol else '')
    if 'molecule_structures' in mol and type(mol['molecule_structures'])==dict:
      mol_struct = mol['molecule_structures']
      for tag in struct_tags:
        vals.append(str(mol_struct[tag]) if tag in mol_struct else '')
    if 'molecule_properties' in mol and type(mol['molecule_properties'])==dict:
      mol_props = mol['molecule_properties']
      for tag in prop_tags:
        vals.append(str(mol_props[tag]) if tag in mol_props else '')

    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_mol: %d'%(n_mol))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))

#############################################################################
def ListMolecules(api_host, api_base_path, only_drug, skip, nmax, fout):
  '''Ignore properties and synonyms here.'''
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None;
  #NCHUNK=1 #DEBUG
  url_next=(api_base_path+'/molecule.json?limit=%d'%NCHUNK)
  if only_drug:
    url_next+=('&max_phase=4')
  while True:
    rval=rest_utils.GetURL('https://'+api_host+url_next,parse_json=True)
    logging.debug(json.dumps(rval,indent=2))
    if not rval or type(rval) != dict:
      n_err+=1
      logging.error('%s'%str(rval))
      break
    mols=rval['molecules'] if 'molecules' in rval else []
    for mol in mols:
      logging.debug(json.dumps(mol,indent=2))
      n_mol+=1
      if n_mol==1:
        tags = sorted(mol.keys())
        for tag in tags[:]:
          if type(mol[tag]) in (dict, list, tuple):
            tags.remove(tag)
        struct_tags = sorted(mol['molecule_structures'].keys())
        prop_tags = sorted(mol['molecule_properties'].keys())
        fout.write('\t'.join(tags+struct_tags+prop_tags+['parent_chembl_id'])+'\n')
      logging.debug(json.dumps(mol,sort_keys=True,indent=2))
      vals=[]
      if 'molecule_hierarchy' in mol and type(mol['molecule_hierarchy'])==dict:
        mol_hier = mol['molecule_hierarchy']
        vals.append(str(mol_hier['parent_chembl_id']) if 'parent_chembl_id' in mol_hier else '')
      for tag in tags:
        vals.append(str(mol[tag]) if tag in mol else '')
      if 'molecule_structures' in mol and type(mol['molecule_structures'])==dict:
        mol_struct = mol['molecule_structures']
        for tag in struct_tags:
          vals.append(str(mol_struct[tag]) if tag in mol_struct else '')
      if 'molecule_properties' in mol and type(mol['molecule_properties'])==dict:
        mol_props = mol['molecule_properties']
        for tag in prop_tags:
          vals.append(str(mol_props[tag]) if tag in mol_props else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_mol%1000==0:
      logging.info('%d mols / %s total'%(n_mol,str(total_count) if total_count else '?'))
    if not url_next: break

  logging.info('n_mol: %d'%n_mol)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#
#############################################################################
### /chemblws/compounds/stdinchikey/QFFGVLORLPOAEC-SNVBAGLBSA-N
def GetInchi2Compound(base_url, ids, fout):
  """Requires InChI key."""
  tags = ['chemblId', 'stdInChiKey', 'smiles', 'molecularFormula', 'species', 'knownDrug', 'preferredCompoundName', 'synonyms', 'molecularWeight' ]
  n_qry=0; n_out=0; n_err=0; 
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    n_qry+=1
    mol = rest_utils.GetURL(base_url+'/compounds/stdinchikey/%s.json'%id_this, parse_json=True)
    if not mol or type(mol) is not dict:
      n_err+=1
      continue
    elif 'compound' not in mol:
      n_err+=1
      continue
    cpd = mol['compound']
    vals = [str(cpd[tag]) if tag in cpd else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))

#############################################################################
