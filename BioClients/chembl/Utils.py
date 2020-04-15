#!/usr/bin/env python3
"""
Utility functions for ChEMBL REST API.
See: https://www.ebi.ac.uk/chembldb/index.php/ws
"""
###
import sys,os,re,json,urllib.parse,logging
#
from ..util import rest_utils
#
NCHUNK=100
#
##############################################################################
def Status(base_url):
  rval=rest_utils.GetURL(base_url+'/status.json',parse_json=True)
  db_ver = rval['chembl_db_version'] if 'chembl_db_version' in rval else ''
  api_ver = rval['api_version'] if 'api_version' in rval else ''
  status = rval['status'] if 'status' in rval else ''
  logging.debug(json.dumps(rval,sort_keys=True,indent=2))
  return api_ver, db_ver, status

#############################################################################
def GetTargetByUniprot(base_url, ids, fout):
  n_out=0;
  ids_chembl = set()
  fout.write("UniprotId\ttarget_chembl_id\n")
  for uniprot in ids:
    id_chembl=None
    rval = rest_utils.GetURL(base_url+'/target.json?target_components__accession=%s'%uniprot, parse_json=True)
    targets = rval['targets'] if 'targets' in rval else []
    for target in targets:
      id_chembl = target['target_chembl_id']
      ids_chembl.add(id_chembl)
      fout.write("%s\t\%s\n"%(uniprot, id_chembl))
      n_out+=1
    if len(ids_chembl)>1:
      logging.info('Uniprot ambiguous: %s'%(uniprot))
    for id_chembl in list(ids_chembl):
      logging.debug('Uniprot: %s -> ChEMBL: %s'%(uniprot, id_chembl))
  logging.info('n_out: %d'%(n_out))

#############################################################################
def GetActivity(api_host, api_base_path, ids, resource, pmin, fout):
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
  n_tgt=0; n_cmt=0; n_out=0; tags=None;
  url_next = (api_base_path+'/target.json?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    tgts = rval['targets'] if rval and 'targets' in rval else []
    for tgt in tgts:
      logging.debug(json.dumps(tgt, indent=2))
      n_tgt+=1
      if not tags:
        tags = sorted(tgt.keys())
        for tag in tags[:]:
          if type(tgt[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.info('Ignoring field (%s): "%s"'%(type(tgt[tag]), tag))
        tags.extend(['component_count', 'accession'])
        fout.write('\t'.join(tags)+'\n')
      vals = [str(tgt[tag]) if tag in tgt else '' for tag in tags]
      if 'target_components' in tgt and tgt['target_components']:
        cmts = tgt['target_components']
        n_cmt+=len(cmts)
        vals.append('%d'%len(cmts))
        vals.append(cmts[0]['accession'] if len(cmts)==1 else '')
      else:
        logging.debug('no-component target: %s'%vals[0])
        vals.extend(['', ''])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    meta = rval['page_meta'] if rval and 'page_meta' in rval else {}
    total_count = meta['total_count'] if 'total_count' in meta else None
    url_next = meta['next'] if 'next' in meta else None
    if n_tgt%1000==0:
      logging.info('%d targets / %s total'%(n_tgt, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_targets: %d; n_target_components: %d; n_out: %d'%(n_tgt, n_cmt, n_out))

#############################################################################
def GetTarget(base_url, ids, fout):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_qry=0; n_tgt=0; n_cmt=0; n_out=0; tags=None;
  for id_this in ids:
    n_qry+=1
    tgt = rest_utils.GetURL(base_url+'/target/%s.json'%id_this, parse_json=True)
    if not tgt: continue
    n_tgt+=1
    if n_tgt==1 or not tags:
      tags = sorted(tgt.keys())
      for tag in tags[:]:
        if type(tgt[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.info('Ignoring field (%s): "%s"'%(type(tgt[tag]), tag))
      tags.extend(['component_count', 'accession'])
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(tgt,sort_keys=True,indent=2))
    vals = [str(tgt[tag]) if tag in tgt else '' for tag in tags]
    if 'target_components' in tgt and tgt['target_components']:
      cmts = tgt['target_components']
      n_cmt+=len(cmts)
      vals.append('%d'%len(cmts))
      vals.append(str(cmts[0]['accession']) if len(cmts)==1 else '')
    else:
      logging.debug('no-component target: %s'%vals[0])
      vals.extend(['', ''])
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_qry: %d; n_targets: %d; n_target_components: %d; n_out: %d'%(n_qry, n_tgt, n_cmt, n_out))

#############################################################################
def GetDocument(base_url, ids, fout):
  n_qry=0; n_doc=0; n_pmid=0; n_doi=0; n_out=0; tags=None;
  for id_this in ids:
    n_qry+=1
    doc = rest_utils.GetURL(base_url+'/document/%s.json'%id_this, parse_json=True)
    if doc:
      n_doc+=1
      if not tags:
        tags = list(doc.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(doc, sort_keys=True, indent=2))
      if 'pubmed_id' in tags and doc[tag]: n_pmid+=1
      if 'doi' in tags and doc[tag]: n_doi+=1
      vals = [str(doc[tag]) if tag in doc else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
  logging.info('n_qry: %d; n_docs: %d; n_pmid: %d; n_doi: %d; n_out: %d'%(n_qry, n_doc, n_pmid, n_doi, n_out))

#############################################################################
def ListSources(base_url, fout):
  n_out=0; tags=None; source_map={};
  rval = rest_utils.GetURL((base_url+'/source.json'), parse_json=True)
  sources = rval['sources'] if 'sources' in rval else []
  for source in sources:
    if not tags:
      tags = list(source.keys())
      fout.write('\t'.join(tags)+'\n')
    source_map[source['src_id']] = source
  for src_id in sorted(source_map.keys()):
    source = source_map[src_id]
    vals = [str(source[tag]) if tag in source else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_out: %d'%n_out)

#############################################################################
def ListCellLines(api_host, api_base_path, fout):
  n_cell=0; n_clo=0; n_efo=0; n_out=0; tags=None;
  url_next = (api_base_path+'/cell_line.json')
  rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  cells = rval['cell_lines'] if 'cell_lines' in rval else []
  for cell in cells:
    n_cell+=1
    if not tags:
      tags = list(cell.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(cell, sort_keys=True, indent=2))
    if 'clo_id' in cell and cell['clo_id']: n_clo+=1
    if 'efo_id' in cell and cell['efo_id']: n_efo+=1
    vals = [str(cell[tag]) if tag in cell else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_cell: %d; n_clo: %d; n_efo: %d; n_out: %d'%(n_cell,n_clo,n_efo,n_out))

#############################################################################
def ListDrugIndications(api_host, api_base_path, fout):
  n_din=0; n_efo=0; n_out=0; tags=None;
  url_next = (api_base_path+'/drug_indication.json')
  rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  dins = rval['drug_indications'] if 'drug_indications' in rval else []
  for din in dins:
    n_din+=1
    if not tags:
      tags = list(din.keys())
      for tag in tags[:]:
        if type(din[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.info('Ignoring field (%s): "%s"'%(type(din[tag]), tag))
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(din, sort_keys=True, indent=2))
    if 'efo_id' in din and din['efo_id']: n_efo+=1
    vals = [str(din[tag]) if tag in din else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_din: %d; n_efo: %d; n_out: %d'%(n_din, n_efo, n_out))

#############################################################################
def ListTissues(api_host, api_base_path, fout):
  n_tissue=0; n_bto=0; n_efo=0; n_caloha=0; n_uberon=0; n_out=0; tags=None;
  url_next = (api_base_path+'/tissue.json')
  rval = rest_utils.GetURL('https://'+api_host+url_next,parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  tissues = rval['tissues'] if 'tissues' in rval else []
  for tissue in tissues:
    n_tissue+=1
    if not tags:
      tags = list(tissue.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(tissue, sort_keys=True, indent=2))
    if 'bto_id' in tissue and tissue['bto_id']: n_bto+=1
    if 'efo_id' in tissue and tissue['efo_id']: n_efo+=1
    if 'uberon_id' in tissue and tissue['uberon_id']: n_uberon+=1
    if 'caloha_id' in tissue and tissue['caloha_id']: n_caloha+=1
    vals = [str(tissue[tag]) if tag in tissue else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_tissue: %d; n_bto: %d; n_efo: %d; n_caloha: %d; n_uberon: %d; n_out: %d'%(n_tissue, n_bto, n_efo, n_caloha, n_uberon, n_out))

#############################################################################
def ListMechanisms(base_url, fout):
  n_mechanism=0; n_out=0; tags=None;
  url = (base_url+'/mechanism.json')
  rval = rest_utils.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  if not rval:
    logging.error("No mechanisms.")
    return
  mechanisms = rval['mechanisms'] if 'mechanisms' in rval else []
  for mechanism in mechanisms:
    n_mechanism+=1
    if not tags:
      tags = list(mechanism.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(mechanism, sort_keys=True, indent=2))
    vals = [str(mechanism[tag]) if tag in mechanism else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_mechanism: %d; n_out: %d'%(n_mechanism, n_out))

#############################################################################
def ListDocuments(api_host, api_base_path, skip, nmax, fout):
  n_doc=0; n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None;
  url_next = (api_base_path+'/document.json?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    docs = rval['documents'] if 'documents' in rval else []
    for doc in docs:
      n_doc+=1
      if not tags:
        tags = list(doc.keys())
        if 'abstract' in tags: tags.remove('abstract') #unnecessary, verbose
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(doc, sort_keys=True, indent=2))
      if 'pubmed_id' in tags and doc['pubmed_id']: n_pmid+=1
      if 'doi' in tags and doc['doi']: n_doi+=1
      vals = [str(doc[tag]) if tag in doc else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if nmax and n_doc>=nmax: break
    if nmax and n_doc>=nmax: break
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_doc%1000==0:
      logging.info('%d docs / %s total'%(n_doc,str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_doc: %d; n_pmid: %d; n_doi: %d; n_out: %d'%(n_doc, n_pmid, n_doi, n_out))
  
#############################################################################
def GetAssay(base_url, ids, fout):
  n_out=0; tags=None;
  for id_this in ids:
    assay = rest_utils.GetURL(base_url+'/assay/%s.json'%id_this, parse_json=True)
    if not assay:
      continue
    if not tags:
      tags = list(assay.keys())
      for tag in tags[:]:
        if type(mol[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.info('Ignoring field (%s): "%s"'%(type(mol[tag]), tag))
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(assay[tag]) if tag in assay else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListAssays(api_host, api_base_path, skip, nmax, fout):
  n_ass=0; n_out=0; tags=None;
  url_next = (api_base_path+'/assay.json?offset=%d&limit=%d'%(skip, NCHUNK))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    assays = rval['assays'] if 'assays' in rval else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = list(assay.keys())
        for tag in tags[:]:
          if type(assay[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.info('Ignoring field (%s): "%s"'%(type(assay[tag]), tag))
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]) if tag in assay else '') for tag in tags]
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
  logging.info('n_out: %d'%(n_out))

#############################################################################
def SearchAssays(api_host, api_base_path, asrc, atype, skip, nmax, fout):
  '''Select assays based on source and optionally type.'''
  n_ass=0; n_out=0; tags=None;
  url_next = (api_base_path+'/assay.json'+'?offset=%d&limit=%d'%(skip, NCHUNK))
  if asrc: url_next+=('&src_id=%d'%(asrc))
  if atype: url_next+=('&assay_type=%s'%(atype))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    assays = rval['assays'] if 'assays' in rval else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = list(assay.keys())
        for tag in tags[:]:
          if type(assay[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.info('Ignoring field (%s): "%s"'%(type(assay[tag]), tag))
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]) if tag in assay else '') for tag in tags]
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
  logging.info('n_assay: %d; n_out: %d'%(n_ass, n_out))

##############################################################################
def GetMolecule(base_url, ids, fout):
  '''Ignore molecule_synonyms.'''
  n_out=0; tags=None; struct_tags=None; prop_tags=None;
  for id_this in ids:
    mol = rest_utils.GetURL(base_url+'/molecule/%s.json'%id_this, parse_json=True)
    if not mol: continue
    if not tags:
      tags = sorted(list(mol.keys()))
      for tag in tags[:]:
        if type(mol[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.info('Ignoring field (%s): "%s"'%(type(mol[tag]), tag))
      struct_tags = sorted(mol['molecule_structures'].keys())
      struct_tags.remove('molfile')
      prop_tags = sorted(mol['molecule_properties'].keys())
      fout.write('\t'.join(tags+struct_tags+prop_tags+['parent_chembl_id'])+'\n')
    logging.debug(json.dumps(mol, sort_keys=True, indent=2))
    vals = [(mol['molecule_hierarchy']['parent_chembl_id'] if 'molecule_hierarchy' in mol and 'parent_chembl_id' in mol['molecule_hierarchy'] else '')]
    vals.extend([(str(mol[tag]) if tag in mol else '') for tag in tags])
    vals.extend([(str(mol['molecule_structures'][tag]) if 'molecule_structures' in mol and tag in mol['molecule_structures'] else '') for tag in struct_tags])
    vals.extend([(str(mol['molecule_properties'][tag]) if 'molecule_properties' in mol and tag in mol['molecule_properties'] else '') for tag in prop_tags])
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListMolecules(api_host, api_base_path, dev_phase, skip, nmax, fout):
  '''Ignore synonyms here.'''
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None;
  url_next=(api_base_path+'/molecule.json?limit=%d'%NCHUNK)
  if skip: url_next+=('&offset=%d'%skip)
  if dev_phase: url_next+=('&max_phase=%d'%dev_phase)
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    mols = rval['molecules'] if 'molecules' in rval else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not tags:
        tags = sorted(mol.keys())
        for tag in tags[:]:
          if type(mol[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.info('Ignoring field (%s): "%s"'%(type(mol[tag]), tag))
        struct_tags = sorted(mol['molecule_structures'].keys())
        struct_tags.remove('molfile')
        prop_tags = sorted(mol['molecule_properties'].keys())
        fout.write('\t'.join(tags+struct_tags+prop_tags+['parent_chembl_id'])+'\n')
      vals = [(mol['molecule_hierarchy']['parent_chembl_id'] if 'molecule_hierarchy' in mol and mol['molecule_hierarchy'] and 'parent_chembl_id' in mol['molecule_hierarchy'] else '')]
      vals.extend([(str(mol[tag]) if tag in mol else '') for tag in tags])
      vals.extend([(str(mol['molecule_structures'][tag]) if 'molecule_structures' in mol and mol['molecule_structures'] and tag in mol['molecule_structures'] else '') for tag in struct_tags])
      vals.extend([(str(mol['molecule_properties'][tag]) if 'molecule_properties' in mol and mol['molecule_properties'] and tag in mol['molecule_properties'] else '') for tag in prop_tags])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_out%1000==0:
      logging.info('%d mols / %s total'%(n_out, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListDrugs(api_host, api_base_path, skip, nmax, fout):
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None;
  url_next = (api_base_path+'/drug.json?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    mols = rval['drugs'] if 'drugs' in rval else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not tags:
        tags = sorted(mol.keys())
        for tag in tags[:]:
          if type(mol[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.info('Ignoring field (%s): "%s"'%(type(mol[tag]), tag))
        struct_tags = sorted(mol['molecule_structures'].keys())
        struct_tags.remove('molfile')
        prop_tags = sorted(mol['molecule_properties'].keys())
        fout.write('\t'.join(tags+struct_tags+prop_tags+['parent_chembl_id'])+'\n')
      vals = [(mol['molecule_hierarchy']['parent_chembl_id'] if 'molecule_hierarchy' in mol and mol['molecule_hierarchy'] and 'parent_chembl_id' in mol['molecule_hierarchy'] else '')]
      vals.extend([(str(mol[tag]) if tag in mol else '') for tag in tags])
      vals.extend([(str(mol['molecule_structures'][tag]) if 'molecule_structures' in mol and mol['molecule_structures'] and tag in mol['molecule_structures'] else '') for tag in struct_tags])
      vals.extend([(str(mol['molecule_properties'][tag]) if 'molecule_properties' in mol and mol['molecule_properties'] and tag in mol['molecule_properties'] else '') for tag in prop_tags])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    meta = rval['page_meta'] if 'page_meta' in rval else {}
    url_next = meta['next'] if 'next' in meta else None
    total_count = meta['total_count'] if 'total_count' in meta else None
    if n_out%1000==0:
      logging.info('%d mols / %s total'%(n_out, str(total_count) if total_count else '?'))
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

##############################################################################
def SearchMoleculeByName(base_url, ids, fout):
  """IDs should be names/synonyms."""
  n_out=0; n_notfound=0; synonym_tags=None;
  tags = ["molecule_chembl_id"]
  for id_this in ids:
    rval = rest_utils.GetURL((base_url+'/molecule/search?q=%s'%urllib.parse.quote(id_this)), headers={'Accept':'application/json'}, parse_json=True)
    if not rval:
      logging.info('Not found: "{0}"'.format(id_this))
      n_notfound+=1
      continue
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    mols = rval["molecules"] if "molecules" in rval else []
    for mol in mols:
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      synonyms = mol["molecule_synonyms"] if "molecule_synonyms" in mol else []
      for synonym in synonyms:
        if not synonym_tags:
          synonym_tags = list(synonym.keys())
          fout.write('\t'.join(tags+synonym_tags)+'\n')

        molecule_synonym = synonym["molecule_synonym"] if "molecule_synonym" in synonym else ""
        if not re.search(id_this, molecule_synonym, re.I):
          continue

        vals = [(mol['molecule_chembl_id'] if 'molecule_chembl_id' in mol else '')]
        vals.extend([(str(synonym[tag]) if tag in synonym else '') for tag in synonym_tags])
        fout.write(('\t'.join(vals))+'\n')
        n_out+=1
  logging.info('n_in: %d; n_found: %d; n_out: %d'%(len(ids), len(ids)-n_notfound, n_out))


#############################################################################
def GetMoleculeByInchikey(base_url, ids, fout):
  """Requires InChI key, e.g. "QFFGVLORLPOAEC-SNVBAGLBSA-N"."""
  tags = ['chemblId', 'stdInChiKey', 'smiles', 'molecularFormula', 'species', 'knownDrug', 'preferredCompoundName', 'synonyms', 'molecularWeight' ]
  n_qry=0; n_out=0;
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    n_qry+=1
    mol = rest_utils.GetURL(base_url+'/compounds/stdinchikey/%s.json'%id_this, parse_json=True)
    if not mol: continue
    cpd = mol['compound'] if 'compound' in mol else None
    if not cpd: continue
    vals = [(str(cpd[tag]) if tag in cpd else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_qry: %d; n_out: %d'%(n_qry, n_out))

#############################################################################
