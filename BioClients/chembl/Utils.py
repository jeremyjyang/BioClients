#!/usr/bin/env python3
"""
Utility functions for ChEMBL REST API.
https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
http://chembl.blogspot.com/2015/02/using-new-chembl-web-services.html
"""
###
import sys,os,re,json,time,urllib.parse,logging,tqdm
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
  '''Get activity data and necessary references only, due to size concerns.  resource = assay|target|molecule.  Filter on pChEMBL value, standardized negative log molar half-max response activity.'''
  n_act=0; n_out=0; n_pval=0; n_pval_ok=0; tags=None;
  for id_this in ids:
    url_next =( api_base_path+'/activity.json?%s_chembl_id=%s&limit=%d'%(resource,id_this,NCHUNK))
    while True:
      rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
      acts = rval['activities'] if 'activities' in rval else []
      for act in acts:
        logging.debug(json.dumps(act, sort_keys=True, indent=2))
        n_act+=1
        if not tags:
          tags = list(act.keys())
          for tag in tags[:]:
            if type(act[tag]) in (dict, list, tuple):
              tags.remove(tag)
              logging.debug('Ignoring field ({0}): "{1}"'.format(type(act[tag]), tag))
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(act[tag]) if tag in act else '') for tag in tags]
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
      total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
      if n_act%1000==0: logging.info('%d/%s act/total'%(n_act, total_count))
      url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
      if not url_next: break
  logging.info('n_qry: %d; n_act: %d; n_out: %d'%(len(ids), n_act, n_out))
  if pmin is not None:
    logging.info('n_pval: %d; n_pval_ok: %d; pVals missing: %d'%(n_pval,n_pval_ok,n_act-n_pval))

#############################################################################
def GetActivityProperties(base_url, ids, fout):
  n_out=0; tags=None;
  for id_this in ids:
    act = rest_utils.GetURL((base_url+'/activity/%s.json'%(id_this)), parse_json=True)
    assay_chembl_id = act['assay_chembl_id'] if 'assay_chembl_id' in act else ""
    molecule_chembl_id = act['molecule_chembl_id'] if 'molecule_chembl_id' in act else ""
    props = act['activity_properties'] if 'activity_properties' in act else []
    for prop in props:
      if not tags:
        tags = list(prop.keys())
        fout.write('\t'.join(['activity_id', 'assay_chembl_id', 'molecule_chembl_id']+tags)+'\n')
      logging.debug(json.dumps(prop, sort_keys=True, indent=2))
      vals = [str(prop[tag]) if tag in prop else '' for tag in tags]
      fout.write(('\t'.join([id_this, assay_chembl_id, molecule_chembl_id]+vals))+'\n')
      n_out+=1
  logging.info('n_qry: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListTargets(api_host, api_base_path, skip, nmax, fout):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; tags=None; tq=None;
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
            logging.debug('Ignoring field ({0}): "{1}"'.format(type(tgt[tag]), tag))
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
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tgts")
    if n_tgt%1000==0: logging.info('%d/%s tgt/total'%(n_tgt, total_count))
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_targets: %d; n_target_components: %d; n_out: %d'%(n_tgt, n_cmt, n_out))

#############################################################################
def GetTarget(base_url, ids, fout):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; tags=None;
  for id_this in ids:
    tgt = rest_utils.GetURL(base_url+'/target/%s.json'%id_this, parse_json=True)
    if not tgt:
      logging.error('Not found: "%s"'%id_this)
      continue
    n_tgt+=1
    if n_tgt==1 or not tags:
      tags = sorted(tgt.keys())
      for tag in tags[:]:
        if type(tgt[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug('Ignoring field ({0}): "{1}"'.format(type(tgt[tag]), tag))
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
  logging.info('n_qry: %d; n_targets: %d; n_target_components: %d; n_out: %d'%(len(ids), n_tgt, n_cmt, n_out))

#############################################################################
def GetTargetComponents(base_url, ids, fout):
  n_tgt=0; n_out=0; tags=[]; cmt_tags=[];
  for id_this in ids:
    tgt = rest_utils.GetURL(base_url+'/target/%s.json'%id_this, parse_json=True)
    if not tgt: continue
    n_tgt+=1
    vals = [str(tgt[tag]) if tag in tgt else '' for tag in tags]
    cmts = tgt['target_components'] if 'target_components' in tgt and tgt['target_components'] else []
    if not cmts: continue
    for cmt in cmts:
      logging.debug(json.dumps(cmt, indent=2))
      if not tags:
        for tag in tgt.keys():
          if type(tgt[tag]) not in (dict, list, tuple):
            tags.append(tag)
        for tag in cmt.keys():
          if type(cmt[tag]) not in (dict, list, tuple):
            cmt_tags.append(tag)
        fout.write('\t'.join(tags+cmt_tags)+'\n')

      vals = [(str(tgt[tag]) if tag in tgt else '') for tag in tags]+[(str(cmt[tag]) if tag in cmt else '') for tag in cmt_tags]

      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
  logging.info('n_qry: %d; n_targets: %d; n_out: %d'%(len(ids), n_tgt, n_out))

#############################################################################
def GetDocument(base_url, ids, fout):
  n_pmid=0; n_doi=0; n_out=0; tags=None;
  for id_this in ids:
    doc = rest_utils.GetURL(base_url+'/document/%s.json'%id_this, parse_json=True)
    if not doc:
      logging.error('Not found: "%s"'%id_this)
      continue
    if not tags:
      tags = list(doc.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(doc, sort_keys=True, indent=2))
    if 'pubmed_id' in tags and doc['pubmed_id']: n_pmid+=1
    if 'doi' in tags and doc['doi']: n_doi+=1
    vals = [str(doc[tag]) if tag in doc else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  logging.info('n_qry: %d; n_pmid: %d; n_doi: %d; n_out: %d'%(len(ids), n_pmid, n_doi, n_out))

#############################################################################
def ListSources(api_host, api_base_path, fout):
  n_out=0; tags=None;
  url_next = (api_base_path+'/source.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    sources = rval['sources'] if 'sources' in rval else []
    for source in sources:
      if not tags:
        tags = list(source.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(source, sort_keys=True, indent=2))
      vals = [str(source[tag]) if tag in source else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d'%n_out)

#############################################################################
def ListCellLines(api_host, api_base_path, fout):
  n_clo=0; n_efo=0; n_out=0; tags=None;
  url_next = (api_base_path+'/cell_line.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    cells = rval['cell_lines'] if 'cell_lines' in rval else []
    for cell in cells:
      if not tags:
        tags = list(cell.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(cell, sort_keys=True, indent=2))
      if 'clo_id' in cell and cell['clo_id']: n_clo+=1
      if 'efo_id' in cell and cell['efo_id']: n_efo+=1
      vals = [str(cell[tag]) if tag in cell else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d; n_clo: %d; n_efo: %d'%(n_out, n_clo, n_efo))

#############################################################################
def ListOrganisms(api_host, api_base_path, fout):
  n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/organism.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    orgs = rval['organisms'] if 'organisms' in rval else []
    for org in orgs:
      if not tags:
        tags = list(org.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(org, sort_keys=True, indent=2))
      vals = [str(org[tag]) if tag in org else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListProteinClasses(api_host, api_base_path, fout):
  n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/protein_class.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    pcls = rval['protein_classes'] if 'protein_classes' in rval else []
    for pcl in pcls:
      if not tags:
        tags = list(pcl.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(pcl, sort_keys=True, indent=2))
      vals = [str(pcl[tag]) if tag in pcl else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListDrugIndications(api_host, api_base_path, skip, nmax, fout):
  n_efo=0; n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/drug_indication.json?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    dins = rval['drug_indications'] if 'drug_indications' in rval else []
    for din in dins:
      if not tags:
        tags = list(din.keys())
        for tag in tags[:]:
          if type(din[tag]) in (dict, list, tuple):
            tags.remove(tag)
          logging.debug('Ignoring field ({0}): "{1}"'.format(type(din[tag]), tag))
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(din, sort_keys=True, indent=2))
      if 'efo_id' in din and din['efo_id']: n_efo+=1
      vals = [str(din[tag]) if tag in din else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="inds")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d; n_efo: %d'%(n_out, n_efo))

#############################################################################
def ListTissues(api_host, api_base_path, fout):
  n_bto=0; n_efo=0; n_caloha=0; n_uberon=0; n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/tissue.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    tissues = rval['tissues'] if 'tissues' in rval else []
    for tissue in tissues:
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
      if tq is not None: tq.update()
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tissues")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d; n_bto: %d; n_efo: %d; n_caloha: %d; n_uberon: %d'%(n_out, n_bto, n_efo, n_caloha, n_uberon))

#############################################################################
def ListMechanisms(api_host, api_base_path, fout):
  n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/mechanism.json')
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    mechs = rval['mechanisms'] if 'mechanisms' in rval else []
    for mech in mechs:
      if not tags:
        tags = list(mech.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(mech, sort_keys=True, indent=2))
      vals = [str(mech[tag]) if tag in mech else '' for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mechs")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListDocuments(api_host, api_base_path, skip, nmax, fout):
  n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None; tq=None;
  url_next = (api_base_path+'/document.json?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest_utils.GetURL('https://'+api_host+url_next, parse_json=True)
    if not rval: break
    docs = rval['documents'] if 'documents' in rval else []
    for doc in docs:
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
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="docs")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d; n_pmid: %d; n_doi: %d'%(n_out, n_pmid, n_doi))

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
        if type(assay[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug('Ignoring field ({0}): "{1}"'.format(type(assay[tag]), tag))
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(assay[tag]) if tag in assay else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListAssays(api_host, api_base_path, skip, nmax, fout):
  n_ass=0; n_out=0; tags=None; tq=None;
  url_next = (api_base_path+'/assay.json?offset=%d&limit=%d'%(skip, NCHUNK))
  t0 = time.time()
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
            logging.debug('Ignoring field ({0}): "{1}"'.format(type(assay[tag]), tag))
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]).replace('\t', ' ') if tag in assay else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: {}'.format(n_out))
  logging.info('Elapsed time: {}'.format(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

#############################################################################
def SearchAssays(api_host, api_base_path, asrc, atype, skip, nmax, fout):
  '''Select assays based on source and optionally type.'''
  n_ass=0; n_out=0; tags=None; tq=None;
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
            logging.debug('Ignoring field ({0}): "{1}"'.format(type(assay[tag]), tag))
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]) if tag in assay else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
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
          logging.debug('Ignoring field ({0}): "{1}"'.format(type(mol[tag]), tag))
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
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; tq=None;
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
            logging.debug('Ignoring field ({0}): "{1}"'.format(type(mol[tag]), tag))
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
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mols")
    if n_out%1000==0: logging.info('%d/%s out/total'%(n_out, total_count))
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
    if not url_next: break
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListDrugs(api_host, api_base_path, skip, nmax, fout):
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; tq=None;
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
            logging.debug('Ignoring field ({0}): "{1}"'.format(type(mol[tag]), tag))
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
      if tq is not None: tq.update()
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    total_count = rval['page_meta']['total_count'] if 'page_meta' in rval and 'total_count' in rval['page_meta'] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="drugs")
    url_next = rval['page_meta']['next'] if 'page_meta' in rval and 'next' in rval['page_meta'] else None
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
  """Requires InChI key, e.g. "GHBOEFUAGSHXPO-XZOTUCIWSA-N"."""
  n_out=0; tags=[]; struct_tags=[];
  for id_this in ids:
    mol = rest_utils.GetURL(base_url+'/molecule/%s.json'%id_this, parse_json=True)
    if not mol:
      continue
    struct = mol['molecule_structures'] if 'molecule_structures' in mol else None
    if not struct: continue
    if not tags:
      for tag in mol.keys():
        if type(mol[tag]) not in (list,dict): tags.append(tag)
      for tag in struct.keys():
        if type(struct[tag]) not in (list,dict): struct_tags.append(tag)
      struct_tags.remove("molfile")
      fout.write('\t'.join(tags+struct_tags)+'\n')
    vals = [(str(mol[tag]) if tag in mol else '') for tag in tags]+[(str(struct[tag]) if tag in struct else '') for tag in struct_tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_qry: %d; n_out: %d; n_not_found: %d'%(len(ids), n_out, len(ids)-n_out))

#############################################################################
