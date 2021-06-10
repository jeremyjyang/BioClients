#!/usr/bin/env python3
"""
Utility functions for ChEMBL REST API.
https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
http://chembl.blogspot.com/2015/02/using-new-chembl-web-services.html
"""
###
import sys,os,re,json,time,urllib.parse,logging,tqdm
import pandas as pd
#
from ..util import rest
#
NCHUNK=100
#
API_HOST="www.ebi.ac.uk"
API_BASE_PATH="/chembl/api/data"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def Status(base_url=BASE_URL, fout=None):
  rval = rest.Utils.GetURL(f"{base_url}/status.json", parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  df = pd.DataFrame({tag:(rval[tag] if tag in rval else "") for tag in rval.keys()})
  if fout is not None: df.to_csv(fout, "\t", index=False)
  else: return df

#############################################################################
def GetTargetByUniprot(ids, base_url=BASE_URL, fout=None):
  n_out=0;
  ids_chembl = set()
  fout.write("UniprotId\ttarget_chembl_id\n")
  for uniprot in ids:
    id_chembl=None
    rval = rest.Utils.GetURL(f"{base_url}/target.json?target_components__accession={uniprot}", parse_json=True)
    targets = rval["targets"] if "targets" in rval else []
    for target in targets:
      id_chembl = target["target_chembl_id"]
      ids_chembl.add(id_chembl)
      fout.write(f"{uniprot}\t\{id_chembl}\n")
      n_out+=1
    if len(ids_chembl)>1:
      logging.info(f"Uniprot ambiguous: {uniprot}")
    for id_chembl in list(ids_chembl):
      logging.debug(f"Uniprot: {uniprot} -> ChEMBL: {id_chembl}")
  logging.info(f"n_out: {n_out}")

#############################################################################
def GetActivity(ids, resource, pmin, skip=0, nmax=None, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Get activity data and necessary references only, due to size concerns.  resource = assay|target|molecule.  Filter on pChEMBL value, standardized negative log molar half-max response activity.'''
  n_act=0; n_out=0; n_pval=0; n_pval_ok=0; tags=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit=resource+"s")
    tq.update()
    url_next = (f"{api_base_path}/activity.json?{resource}_chembl_id={id_this}&limit={NCHUNK}")
    while True:
      rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
      if rval is None: break
      acts = rval["activities"] if "activities" in rval else []
      for act in acts:
        logging.debug(json.dumps(act, sort_keys=True, indent=2))
        n_act+=1
        if not tags:
          tags = list(act.keys())
          for tag in tags[:]:
            if type(act[tag]) in (dict, list, tuple):
              tags.remove(tag)
              logging.debug(f'Ignoring field ({type(act[tag])}): "{tag}"')
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(act[tag]) if tag in act else '') for tag in tags]
        if pmin is not None:
          try:
            pval = float(act["pchembl_value"])
            n_pval+=1
            if pval >= pmin:
              n_pval_ok+=1
              fout.write('\t'.join(vals)+'\n')
              n_out+=1
              logging.debug(f"[{n_act}] pVal ok ({pval:4.1f} >= {pmin:4.1f})")
            else:
              logging.debug(f"[{n_act}] pVal low ({pval:4.1f} < {pmin:4.1f})")
          except:
            logging.debug(f"[{n_act}] pVal missing.")
        else:
          fout.write('\t'.join(vals)+'\n')
          n_out+=1
      total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
      url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
      if not url_next: break
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_act: {n_act}; n_out: {n_out}")
  if pmin is not None:
    logging.info(f"n_pval: {n_pval}; n_pval_ok: {n_pval_ok}; pVals missing: {n_act-n_pval}")

#############################################################################
def GetActivityProperties(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    act = rest.Utils.GetURL((f"{base_url}/activity/{id_this}.json"), parse_json=True)
    assay_chembl_id = act["assay_chembl_id"] if "assay_chembl_id" in act else ""
    molecule_chembl_id = act["molecule_chembl_id"] if "molecule_chembl_id" in act else ""
    props = act["activity_properties"] if "activity_properties" in act else []
    for prop in props:
      if not tags:
        tags = list(prop.keys())
        fout.write('\t'.join(["activity_id", "assay_chembl_id", "molecule_chembl_id"]+tags)+"\n")
      logging.debug(json.dumps(prop, sort_keys=True, indent=2))
      vals = [str(prop[tag]) if tag in prop else "" for tag in tags]
      fout.write(('\t'.join([id_this, assay_chembl_id, molecule_chembl_id]+vals))+'\n')
      n_out+=1
    if nmax and i>=(nmax-skip): break
  logging.info(f"n_qry: {len(ids)}; n_out: {n_out}")

#############################################################################
def ListTargets(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; tags=None; tq=None;
  url_next = (f"{api_base_path}/target.json?limit={NCHUNK}&offset={skip}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    tgts = rval["targets"] if rval and "targets" in rval else []
    for tgt in tgts:
      logging.debug(json.dumps(tgt, indent=2))
      n_tgt+=1
      if not tags:
        tags = sorted(tgt.keys())
        for tag in tags[:]:
          if type(tgt[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field ({type(tgt[tag])}): "{tag}"')
        tags.extend(["component_count", "accession"])
        fout.write('\t'.join(tags)+'\n')
      vals = [str(tgt[tag]) if tag in tgt else "" for tag in tags]
      if "target_components" in tgt and tgt["target_components"]:
        cmts = tgt["target_components"]
        n_cmt+=len(cmts)
        vals.append(f"{len(cmts)}")
        vals.append(cmts[0]["accession"] if len(cmts)==1 else "")
      else:
        logging.debug(f"no-component target: {vals[0]}")
        vals.extend(["", ""])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tgts")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_targets: {n_tgt}; n_target_components: {n_cmt}; n_out: {n_out}")

#############################################################################
def GetTarget(ids, base_url=BASE_URL, fout=None):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; tags=None; tq=None;
  for id_this in ids:
    tgt = rest.Utils.GetURL(f"{base_url}/target/{id_this}.json", parse_json=True)
    if not tgt:
      logging.error(f'Not found: "{id_this}"')
      continue
    n_tgt+=1
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="tgts")
    tq.update()
    if n_tgt==1 or not tags:
      tags = sorted(tgt.keys())
      for tag in tags[:]:
        if type(tgt[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug(f'Ignoring field ({type(tgt[tag])}): "{tag}"')
      tags.extend(["component_count", "accession"])
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(tgt,sort_keys=True,indent=2))
    vals = [str(tgt[tag]) if tag in tgt else "" for tag in tags]
    if "target_components" in tgt and tgt["target_components"]:
      cmts = tgt["target_components"]
      n_cmt+=len(cmts)
      vals.append(f"{len(cmts)}")
      vals.append(str(cmts[0]["accession"]) if len(cmts)==1 else "")
    else:
      logging.debug(f"no-component target: {vals[0]}")
      vals.extend(["", ""])
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_targets: {n_tgt}; n_target_components: {n_cmt}; n_out: {n_out}")

#############################################################################
def GetTargetComponents(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_tgt=0; n_out=0; tags=[]; cmt_tags=[]; df=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit="tgts")
    tq.update()
    tgt = rest.Utils.GetURL(f"{base_url}/target/{id_this}.json", parse_json=True)
    if not tgt: continue
    n_tgt+=1
    vals = [str(tgt[tag]) if tag in tgt else "" for tag in tags]
    cmts = tgt["target_components"] if "target_components" in tgt and tgt["target_components"] else []
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
      df_this = pd.concat([
	pd.DataFrame({tag:[(tgt[tag] if tag in tgt else None)] for tag in tags}),
	pd.DataFrame({tag:[(cmt[tag] if tag in cmt else None)] for tag in cmt_tags})],
	axis=1)
      if fout is None:
        df = pd.concat([df, df_this])
      else:
        df_this.to_csv(fout, "\t", index=False)
      n_out+=df_this.shape[0]
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_targets: {n_tgt}; n_out: {n_out}")
  if fout is None: return df

#############################################################################
def GetDocument(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_pmid=0; n_doi=0; n_out=0; tags=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit="docs")
    tq.update()
    doc = rest.Utils.GetURL(f"{base_url}/document/{id_this}.json", parse_json=True)
    if not doc:
      logging.error(f'Not found: "{id_this}"')
      continue
    if not tags:
      tags = list(doc.keys())
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(doc, sort_keys=True, indent=2))
    if "pubmed_id" in tags and doc["pubmed_id"]: n_pmid+=1
    if "doi" in tags and doc["doi"]: n_doi+=1
    vals = [str(doc[tag]) if tag in doc else "" for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_pmid: {n_pmid}; n_doi: {n_doi}; n_out: {n_out}")

#############################################################################
def ListSources(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; tags=None;
  url_next = (api_base_path+"/source.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    sources = rval["sources"] if "sources" in rval else []
    for source in sources:
      if not tags:
        tags = list(source.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(source, sort_keys=True, indent=2))
      vals = [str(source[tag]) if tag in source else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListCellLines(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_clo=0; n_efo=0; n_out=0; tags=None;
  url_next = (api_base_path+"/cell_line.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    cells = rval["cell_lines"] if "cell_lines" in rval else []
    for cell in cells:
      if not tags:
        tags = list(cell.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(cell, sort_keys=True, indent=2))
      if "clo_id" in cell and cell["clo_id"]: n_clo+=1
      if "efo_id" in cell and cell["efo_id"]: n_efo+=1
      vals = [str(cell[tag]) if tag in cell else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}; n_clo: {n_clo}; n_efo: {n_efo}")

#############################################################################
def ListOrganisms(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; tags=None;
  url_next = (api_base_path+"/organism.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    orgs = rval["organisms"] if "organisms" in rval else []
    for org in orgs:
      if not tags:
        tags = list(org.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(org, sort_keys=True, indent=2))
      vals = [str(org[tag]) if tag in org else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListProteinClasses(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; tags=None;
  url_next = (api_base_path+"/protein_class.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    pcls = rval["protein_classes"] if "protein_classes" in rval else []
    for pcl in pcls:
      if not tags:
        tags = list(pcl.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(pcl, sort_keys=True, indent=2))
      vals = [str(pcl[tag]) if tag in pcl else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListDrugIndications(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_efo=0; n_out=0; tags=None; tq=None;
  url_next = (f"{api_base_path}/drug_indication.json?limit={NCHUNK}&offset={skip}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    dins = rval["drug_indications"] if "drug_indications" in rval else []
    for din in dins:
      if not tags:
        tags = list(din.keys())
        for tag in tags[:]:
          if type(din[tag]) in (dict, list, tuple):
            tags.remove(tag)
          logging.debug(f'Ignoring field ({type(din[tag])}): "{tag}"')
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(din, sort_keys=True, indent=2))
      if "efo_id" in din and din["efo_id"]: n_efo+=1
      vals = [str(din[tag]) if tag in din else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="inds")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_efo: {n_efo}")

#############################################################################
def ListTissues(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_bto=0; n_efo=0; n_caloha=0; n_uberon=0; n_out=0; tags=None; tq=None;
  url_next = (api_base_path+"/tissue.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    tissues = rval["tissues"] if "tissues" in rval else []
    for tissue in tissues:
      if not tags:
        tags = list(tissue.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(tissue, sort_keys=True, indent=2))
      if "bto_id" in tissue and tissue["bto_id"]: n_bto+=1
      if "efo_id" in tissue and tissue["efo_id"]: n_efo+=1
      if "uberon_id" in tissue and tissue["uberon_id"]: n_uberon+=1
      if "caloha_id" in tissue and tissue["caloha_id"]: n_caloha+=1
      vals = [str(tissue[tag]) if tag in tissue else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tissues")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_bto: {n_bto}; n_efo: {n_efo}; n_caloha: {n_caloha}; n_uberon: {n_uberon}")

#############################################################################
def ListMechanisms(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; tags=None; tq=None;
  url_next = (api_base_path+"/mechanism.json")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    mechs = rval["mechanisms"] if "mechanisms" in rval else []
    for mech in mechs:
      if not tags:
        tags = list(mech.keys())
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(mech, sort_keys=True, indent=2))
      vals = [str(mech[tag]) if tag in mech else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mechs")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListDocuments(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None; tq=None;
  url_next = (f"{api_base_path}/document.json?limit={NCHUNK}&offset={skip}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    docs = rval["documents"] if "documents" in rval else []
    for doc in docs:
      if not tags:
        tags = list(doc.keys())
        if "abstract" in tags: tags.remove("abstract") #unnecessary, verbose
        fout.write('\t'.join(tags)+'\n')
      logging.debug(json.dumps(doc, sort_keys=True, indent=2))
      if "pubmed_id" in tags and doc["pubmed_id"]: n_pmid+=1
      if "doi" in tags and doc["doi"]: n_doi+=1
      vals = [str(doc[tag]) if tag in doc else "" for tag in tags]
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="docs")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_pmid: {n_pmid}; n_doi: {n_doi}")

#############################################################################
def GetAssay(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None;
  for id_this in ids:
    assay = rest.Utils.GetURL(f"{base_url}/assay/{id_this}.json", parse_json=True)
    if not assay:
      continue
    if not tags:
      tags = list(assay.keys())
      for tag in tags[:]:
        if type(assay[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug(f'Ignoring field ({type(assay[tag])}): "{tag}"')
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(assay[tag]) if tag in assay else "") for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")

#############################################################################
def ListAssays(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_ass=0; n_out=0; tags=None; tq=None;
  url_next = (f"{api_base_path}/assay.json?offset={skip}&limit={NCHUNK}")
  t0 = time.time()
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    assays = rval["assays"] if "assays" in rval else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = list(assay.keys())
        for tag in tags[:]:
          if type(assay[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field ({type(assay[tag])}): "{tag}"')
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]).replace('\t', " ") if tag in assay else "") for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}""")

#############################################################################
def SearchAssays(asrc, atype, skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Select assays based on source and optionally type.'''
  n_ass=0; n_out=0; tags=None; tq=None;
  url_next = (f"{api_base_path}/assay.json?offset={skip}&limit={NCHUNK}")
  if asrc: url_next+=(f"&src_id={asrc}")
  if atype: url_next+=(f"&assay_type={atype}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    assays = rval["assays"] if "assays" in rval else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = list(assay.keys())
        for tag in tags[:]:
          if type(assay[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field ({type(assay[tag])}): "{tag}"')
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(assay[tag]) if tag in assay else "") for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_assay: {n_ass}; n_out: {n_out}")

##############################################################################
def GetMolecule(ids, base_url=BASE_URL, fout=None):
  '''Ignore molecule_synonyms.'''
  n_out=0; tags=None; struct_tags=None; prop_tags=None; tq=None;
  for id_this in ids:
    mol = rest.Utils.GetURL(f"{base_url}/molecule/{id_this}.json", parse_json=True)
    if not mol: continue
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="mols")
    tq.update()
    if not tags:
      tags = sorted(list(mol.keys()))
      for tag in tags[:]:
        if type(mol[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug(f'Ignoring field ({type(mol[tag])}): "{tag}"')
      struct_tags = sorted(mol["molecule_structures"].keys())
      struct_tags.remove("molfile")
      prop_tags = sorted(mol["molecule_properties"].keys())
      fout.write('\t'.join(tags+struct_tags+prop_tags+["parent_chembl_id"])+'\n')
    logging.debug(json.dumps(mol, sort_keys=True, indent=2))
    vals = [(mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and "parent_chembl_id" in mol["molecule_hierarchy"] else "")]
    vals.extend([(str(mol[tag]) if tag in mol else "") for tag in tags])
    vals.extend([(str(mol["molecule_structures"][tag]) if "molecule_structures" in mol and tag in mol["molecule_structures"] else "") for tag in struct_tags])
    vals.extend([(str(mol["molecule_properties"][tag]) if "molecule_properties" in mol and tag in mol["molecule_properties"] else "") for tag in prop_tags])
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
  if tq is not None: tq.close()
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")

#############################################################################
def ListMolecules(dev_phase, skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Ignore synonyms here.'''
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; tq=None;
  url_next=(f"{api_base_path}/molecule.json?limit={NCHUNK}")
  if skip: url_next+=(f"&offset={skip}")
  if dev_phase: url_next+=(f"&max_phase={dev_phase}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    mols = rval["molecules"] if "molecules" in rval else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not tags:
        tags = sorted(mol.keys())
        for tag in tags[:]:
          if type(mol[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field ({type(mol[tag])}): "{tag}"')
        struct_tags = sorted(mol["molecule_structures"].keys())
        struct_tags.remove("molfile")
        prop_tags = sorted(mol["molecule_properties"].keys())
        fout.write('\t'.join(tags+struct_tags+prop_tags+["parent_chembl_id"])+'\n')
      vals = [(mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and mol["molecule_hierarchy"] and "parent_chembl_id" in mol["molecule_hierarchy"] else "")]
      vals.extend([(str(mol[tag]) if tag in mol else "") for tag in tags])
      vals.extend([(str(mol["molecule_structures"][tag]) if "molecule_structures" in mol and mol["molecule_structures"] and tag in mol["molecule_structures"] else "") for tag in struct_tags])
      vals.extend([(str(mol["molecule_properties"][tag]) if "molecule_properties" in mol and mol["molecule_properties"] and tag in mol["molecule_properties"] else "") for tag in prop_tags])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mols")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")

#############################################################################
def ListDrugs(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; tq=None;
  url_next = (f"{api_base_path}/drug.json?limit={NCHUNK}&offset={skip}")
  while True:
    rval = rest.Utils.GetURL("https://"+api_host+url_next, parse_json=True)
    if not rval: break
    mols = rval["drugs"] if "drugs" in rval else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not tags:
        tags = sorted(mol.keys())
        for tag in tags[:]:
          if type(mol[tag]) in (dict, list, tuple):
            tags.remove(tag)
            logging.debug(f'Ignoring field ({type(mol[tag])}): "{tag}"')
        struct_tags = sorted(mol["molecule_structures"].keys())
        struct_tags.remove("molfile")
        prop_tags = sorted(mol["molecule_properties"].keys())
        fout.write('\t'.join(tags+struct_tags+prop_tags+["parent_chembl_id"])+'\n')
      vals = [(mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and mol["molecule_hierarchy"] and "parent_chembl_id" in mol["molecule_hierarchy"] else "")]
      vals.extend([(str(mol[tag]) if tag in mol else "") for tag in tags])
      vals.extend([(str(mol["molecule_structures"][tag]) if "molecule_structures" in mol and mol["molecule_structures"] and tag in mol["molecule_structures"] else "") for tag in struct_tags])
      vals.extend([(str(mol["molecule_properties"][tag]) if "molecule_properties" in mol and mol["molecule_properties"] and tag in mol["molecule_properties"] else "") for tag in prop_tags])
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
      if tq is not None: tq.update()
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    total_count = rval["page_meta"]["total_count"] if "page_meta" in rval and "total_count" in rval["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="drugs")
    url_next = rval["page_meta"]["next"] if "page_meta" in rval and "next" in rval["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")

##############################################################################
def SearchMoleculeByName(ids, base_url=BASE_URL, fout=None):
  """IDs should be names/synonyms."""
  n_out=0; n_notfound=0; synonym_tags=None;
  tags = ["molecule_chembl_id"]
  for id_this in ids:
    rval = rest.Utils.GetURL(f"{base_url}/molecule/search?q={urllib.parse.quote(id_this)}", headers={"Accept":"application/json"}, parse_json=True)
    if not rval:
      logging.info(f'Not found: "{id_this}"')
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

        vals = [(mol["molecule_chembl_id"] if "molecule_chembl_id" in mol else "")]
        vals.extend([(str(synonym[tag]) if tag in synonym else "") for tag in synonym_tags])
        fout.write(('\t'.join(vals))+'\n')
        n_out+=1
  logging.info(f"n_in: {len(ids)}; n_found: {len(ids)-n_notfound}; n_out: {n_out}")

#############################################################################
def GetMoleculeByInchikey(ids, base_url=BASE_URL, fout=None):
  """Requires InChI key, e.g. "GHBOEFUAGSHXPO-XZOTUCIWSA-N"."""
  n_out=0; tags=[]; struct_tags=[]; df=None; tq=None;
  for id_this in ids:
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="mols")
    tq.update()
    mol = rest.Utils.GetURL(f"{base_url}/molecule/{id_this}.json", parse_json=True)
    if not mol:
      continue
    struct = mol["molecule_structures"] if "molecule_structures" in mol else None
    if not struct: continue
    if not tags:
      for tag in mol.keys():
        if type(mol[tag]) not in (list,dict): tags.append(tag)
      for tag in struct.keys():
        if type(struct[tag]) not in (list,dict): struct_tags.append(tag)
      struct_tags.remove("molfile")
    df_this = pd.concat([
	pd.DataFrame({tag:[(mol[tag] if tag in mol else None)] for tag in tags}),
	pd.DataFrame({tag:[(struct[tag] if tag in struct else None)] for tag in struct_tags})],
	axis=1)
    if fout is None:
      df = pd.concat([df, df_this])
    else:
      df_this.to_csv(fout, "\t", index=False)
    n_out+=1
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_out: {n_out}; n_not_found: {len(ids)-n_out}")
  if fout is None: return df

#############################################################################
