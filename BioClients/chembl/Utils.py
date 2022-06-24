#!/usr/bin/env python3
"""
Utility functions for ChEMBL REST API.
https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
http://chembl.blogspot.com/2015/02/using-new-chembl-web-services.html
"""
###
import sys,os,re,json,time,requests,urllib.parse,logging,tqdm
import pandas as pd
#
NCHUNK=100
#
API_HOST="www.ebi.ac.uk"
API_BASE_PATH="/chembl/api/data"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def Status(base_url=BASE_URL, fout=None):
  response = requests.get(f"{base_url}/status.json")
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  df = pd.DataFrame({tag:(result[tag] if tag in result else "") for tag in result.keys()})
  if fout is not None: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def GetTargetByUniprot(ids, base_url=BASE_URL, fout=None):
  df=None; n_out=0;
  ids_chembl = set()
  fout.write("UniprotId\ttarget_chembl_id\n")
  for id_this in ids:
    id_chembl=None
    response = requests.get(f"{base_url}/target.json?target_components__accession={id_this}")
    result = response.json()
    targets = result["targets"] if "targets" in result else []
    for target in targets:
      id_chembl = target["target_chembl_id"]
      ids_chembl.add(id_chembl)
      fout.write(f"{id_this}\t\{id_chembl}\n")
      n_out+=1
    if len(ids_chembl)>1:
      logging.info(f"Uniprot ambiguous: {id_this}")
    for id_chembl in list(ids_chembl):
      logging.debug(f"Uniprot: {id_this} -> ChEMBL: {id_chembl}")
  logging.info(f"n_out: {n_out}")

#############################################################################
def GetActivity(ids, resource, pmin, skip=0, nmax=None, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Get activity data and necessary references only, due to size concerns.  resource = assay|target|molecule.  Filter on pChEMBL value, standardized negative log molar half-max response activity.'''
  n_act=0; n_out=0; n_pval=0; n_pval_ok=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit=resource+"s")
    tq.update()
    url_next = (f"{api_base_path}/activity.json?{resource}_chembl_id={id_this}&limit={NCHUNK}")
    while True:
      response = requests.get("https://"+api_host+url_next)
      if response.status_code != 200:
        logging.error(f"status_code: {response.status_code}")
        break
      result = response.json()
      acts = result["activities"] if "activities" in result else []
      for act in acts:
        logging.debug(json.dumps(act, sort_keys=True, indent=2))
        n_act+=1
        if not tags:
          tags = list(act.keys())
          for tag in tags[:]:
            if type(act[tag]) in (dict, list, tuple):
              tags.remove(tag)
              logging.debug(f'Ignoring field ({type(act[tag])}): "{tag}"')
        df_this = pd.DataFrame({tag:[(act[tag] if tag in act else None)] for tag in tags})
        pval_ok = bool(pmin is None)
        if pmin is not None:
          try:
            pval = float(act["pchembl_value"])
            n_pval+=1
            if pval >= pmin:
              n_pval_ok+=1
              pval_ok=True;
              logging.debug(f"[{n_act}] pVal ok ({pval:4.1f} >= {pmin:4.1f})")
            else:
              logging.debug(f"[{n_act}] pVal low ({pval:4.1f} < {pmin:4.1f})")
          except:
            logging.debug(f"[{n_act}] pVal missing.")
        if pval_ok:
          if fout is None: df = pd.concat([df, df_this])
          else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
          n_out+=df_this.shape[0]
      total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
      url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
      if not url_next: break
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_act: {n_act}; n_out: {n_out}")
  if pmin is not None:
    logging.info(f"n_pval: {n_pval}; n_pval_ok: {n_pval_ok}; pVals missing: {n_act-n_pval}")
  return df

#############################################################################
def GetActivityProperties(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    response = requests.get(f"{base_url}/activity/{id_this}.json")
    result = response.json()
    assay_chembl_id = result["assay_chembl_id"] if "assay_chembl_id" in result else ""
    molecule_chembl_id = result["molecule_chembl_id"] if "molecule_chembl_id" in result else ""
    props = result["activity_properties"] if "activity_properties" in result else []
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
  n_tgt=0; n_cmt=0; n_out=0; tags=None; df=None; tq=None;
  url_next = (f"{api_base_path}/target.json?limit={NCHUNK}&offset={skip}")
  while True:
    response = requests.get("https://"+api_host+url_next)
    result = response.json()
    tgts = result["targets"] if result and "targets" in result else []
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
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tgts")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_targets: {n_tgt}; n_target_components: {n_cmt}; n_out: {n_out}")

#############################################################################
def GetTarget(ids, base_url=BASE_URL, fout=None):
  '''One row per target.  Ignore synonyms. If one-component, single protein, include UniProt accession.'''
  n_tgt=0; n_cmt=0; n_out=0; tags=None; df=None; tq=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/target/{id_this}.json")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    n_tgt+=1
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="tgts")
    tq.update()
    if n_tgt==1 or not tags:
      tags = sorted(result.keys())
      for tag in tags[:]:
        if type(result[tag]) in (dict, list, tuple):
          tags.remove(tag)
          logging.debug(f'Ignoring field ({type(result[tag])}): "{tag}"')
      tags.extend(["component_count", "accession"])
      fout.write('\t'.join(tags)+'\n')
    logging.debug(json.dumps(result,sort_keys=True,indent=2))
    vals = [str(result[tag]) if tag in result else "" for tag in tags]
    if "target_components" in result and result["target_components"]:
      cmts = result["target_components"]
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
  n_tgt=0; n_out=0; tgt_tags=[]; cmt_tags=[]; df=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit="tgts")
    tq.update()
    response = requests.get(f"{base_url}/target/{id_this}.json")
    result = response.json()
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    logging.debug(json.dumps(result, indent=2))
    n_tgt+=1
    cmts = result["target_components"] if "target_components" in result and result["target_components"] else []
    for cmt in cmts:
      logging.debug(json.dumps(cmt, indent=2))
      if not tgt_tags:
        for tag in result.keys():
          if type(result[tag]) not in (dict, list, tuple):
            tgt_tags.append(tag)
      if not cmt_tags:
        for tag in cmt.keys():
          if type(cmt[tag]) not in (dict, list, tuple):
            cmt_tags.append(tag)
      df_this = pd.concat([
	pd.DataFrame({tag:[(result[tag] if tag in result else None)] for tag in tgt_tags}),
	pd.DataFrame({tag:[(cmt[tag] if tag in cmt else None)] for tag in cmt_tags})],
	axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
    if nmax and i>=(nmax-skip): break
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_targets: {n_tgt}; n_out: {n_out}")
  return df

#############################################################################
def GetDocument(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_pmid=0; n_doi=0; n_out=0; tags=None; df=None; tq=None;
  for i,id_this in enumerate(ids):
    if i<skip: continue
    if not tq: tq = tqdm.tqdm(total=len(ids)-skip, unit="docs")
    tq.update()
    try:
      response = requests.get(f"{base_url}/document/{id_this}.json")
    except Exception as e:
      logging.error(f"{type(e)=}: {e=}")
      continue
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    if not tags:
      tags = [tag for tag in list(result.keys()) if type(result[tag]) not in (dict, list)]
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if "pubmed_id" in tags and result["pubmed_id"]: n_pmid+=1
    if "doi" in tags and result["doi"]: n_doi+=1
    df_this = pd.DataFrame({tag:[(result[tag] if tag in result else None)] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out+=df_this.shape[0]
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_pmid: {n_pmid}; n_doi: {n_doi}; n_out: {n_out}")
  return df

#############################################################################
def ListSources(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; df=None; tags=None;
  url_next = f"{api_base_path}/source.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    sources = result["sources"] if "sources" in result else []
    for source in sources:
      if not tags:
        tags = [tag for tag in list(source.keys()) if type(source[tag]) not in (dict, list)]
      logging.debug(json.dumps(source, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(source[tag] if tag in source else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListCellLines(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_clo=0; n_efo=0; n_out=0; df=None; tags=None;
  url_next = f"{api_base_path}/cell_line.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    cells = result["cell_lines"] if "cell_lines" in result else []
    for cell in cells:
      if not tags:
        tags = [tag for tag in list(cell.keys()) if type(cell[tag]) not in (dict, list)]
      logging.debug(json.dumps(cell, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(cell[tag] if tag in cell else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if "clo_id" in cell and cell["clo_id"]: n_clo+=1
      if "efo_id" in cell and cell["efo_id"]: n_efo+=1
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}; n_clo: {n_clo}; n_efo: {n_efo}")
  return df

#############################################################################
def ListOrganisms(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; df=None; tags=None;
  url_next = f"{api_base_path}/organism.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    orgs = result["organisms"] if "organisms" in result else []
    for org in orgs:
      if not tags:
        tags = [tag for tag in list(org.keys()) if type(org[tag]) not in (dict, list)]
      logging.debug(json.dumps(org, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(org[tag] if tag in org else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListProteinClasses(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; df=None; tags=None;
  url_next = f"{api_base_path}/protein_class.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    pcls = result["protein_classes"] if "protein_classes" in result else []
    for pcl in pcls:
      if not tags:
        tags = [tag for tag in list(pcl.keys()) if type(pcl[tag]) not in (dict, list)]
      logging.debug(json.dumps(pcl, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(pcl[tag] if tag in pcl else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListDrugIndications(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_efo=0; n_out=0; tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/drug_indication.json?limit={NCHUNK}&offset={skip}"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    dins = result["drug_indications"] if "drug_indications" in result else []
    for din in dins:
      if not tags:
        tags = [tag for tag in list(din.keys()) if type(din[tag]) not in (dict, list)]
      logging.debug(json.dumps(din, sort_keys=True, indent=2))
      if "efo_id" in din and din["efo_id"]: n_efo+=1
      df_this = pd.DataFrame({tag:[(din[tag] if tag in din else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="inds")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_efo: {n_efo}")
  return df

#############################################################################
def ListTissues(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_bto=0; n_efo=0; n_caloha=0; n_uberon=0; n_out=0; tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/tissue.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    tissues = result["tissues"] if "tissues" in result else []
    for tissue in tissues:
      if not tags:
        tags = [tag for tag in list(tissue.keys()) if type(tissue[tag]) not in (dict, list)]
      logging.debug(json.dumps(tissue, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(tissue[tag] if tag in tissue else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if "bto_id" in tissue and tissue["bto_id"]: n_bto+=1
      if "efo_id" in tissue and tissue["efo_id"]: n_efo+=1
      if "uberon_id" in tissue and tissue["uberon_id"]: n_uberon+=1
      if "caloha_id" in tissue and tissue["caloha_id"]: n_caloha+=1
      if tq is not None: tq.update()
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="tissues")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_bto: {n_bto}; n_efo: {n_efo}; n_caloha: {n_caloha}; n_uberon: {n_uberon}")
  return df

#############################################################################
def ListMechanisms(api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_out=0; tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/mechanism.json"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    mechs = result["mechanisms"] if "mechanisms" in result else []
    for mech in mechs:
      if not tags:
        tags = [tag for tag in list(mech.keys()) if type(mech[tag]) not in (dict, list)]
      logging.debug(json.dumps(mech, sort_keys=True, indent=2))
      df_this = pd.DataFrame({tag:[(mech[tag] if tag in mech else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mechs")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListDocuments(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_pmid=0; n_doi=0; n_out=0; n_err=0; tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/document.json?limit={NCHUNK}&offset={skip}"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    docs = result["documents"] if "documents" in result else []
    for doc in docs:
      if not tags:
        tags = [tag for tag in list(doc.keys()) if type(doc[tag]) not in (dict, list)]
        if "abstract" in tags: tags.remove("abstract") #unnecessary, verbose
      logging.debug(json.dumps(doc, sort_keys=True, indent=2))
      if "pubmed_id" in tags and doc["pubmed_id"]: n_pmid+=1
      if "doi" in tags and doc["doi"]: n_doi+=1
      df_this = pd.DataFrame({tag:[(doc[tag] if tag in doc else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="docs")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}; n_pmid: {n_pmid}; n_doi: {n_doi}")
  return df

#############################################################################
def GetAssay(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None; tags=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/assay/{id_this}.json")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    if not tags:
      tags = [tag for tag in list(result.keys()) if type(result[tag]) not in (dict, list)]
    df_this = pd.DataFrame({tag:[(result[tag] if tag in result else None)] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out+=df_this.shape[0]
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")
  return df

#############################################################################
def ListAssays(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_ass=0; n_out=0; tags=None; df=None; tq=None;
  url_next = (f"{api_base_path}/assay.json?offset={skip}&limit={NCHUNK}")
  t0 = time.time()
  while True:
    response = requests.get("https://"+api_host+url_next)
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    assays = result["assays"] if "assays" in result else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = [tag for tag in list(assay.keys()) if type(assay[tag]) not in (dict, list)]
      df_this = pd.DataFrame({tag:[(assay[tag] if tag in assay else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}""")
  return df

#############################################################################
def SearchAssays(asrc, atype, skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Select assays based on source and optionally type.'''
  n_ass=0; n_out=0; tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/assay.json?offset={skip}&limit={NCHUNK}"
  if asrc: url_next+=(f"&src_id={asrc}")
  if atype: url_next+=(f"&assay_type={atype}")
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    assays = result["assays"] if "assays" in result else []
    for assay in assays:
      n_ass+=1
      if not tags:
        tags = [tag for tag in list(assay.keys()) if type(assay[tag]) not in (dict, list)]
      df_this = pd.DataFrame({tag:[(assay[tag] if tag in assay else None)] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="assays")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_assay: {n_ass}; n_out: {n_out}")
  return df

##############################################################################
def GetMolecule(ids, base_url=BASE_URL, fout=None):
  '''Ignore molecule_synonyms.'''
  n_out=0; mol_tags=None; struct_tags=None; prop_tags=None; df=None; tq=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/molecule/{id_this}.json")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    mol = response.json()
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="mols")
    tq.update()
    if not mol_tags:
      mol_tags = [tag for tag in sorted(list(mol.keys())) if type(mol[tag]) not in (dict, list)]
    if not struct_tags:
      struct_tags = sorted(mol["molecule_structures"].keys())
      struct_tags.remove("molfile")
    if not prop_tags:
      prop_tags = sorted(mol["molecule_properties"].keys())
    logging.debug(json.dumps(mol, sort_keys=True, indent=2))
    parent_chembl_id = mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and "parent_chembl_id" in mol["molecule_hierarchy"] else ""
    df_this = pd.concat([
	pd.DataFrame({tag:[(mol[tag] if tag in mol else None)] for tag in mol_tags}),
	pd.DataFrame({tag:[(mol["molecule_structures"][tag] if tag in mol["molecule_structures"] else None)] for tag in struct_tags}),
	pd.DataFrame({tag:[(mol["molecule_properties"][tag] if tag in mol["molecule_properties"] else None)] for tag in prop_tags}),
	pd.DataFrame({"parent_chembl_id":[parent_chembl_id]})], axis=1)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out+=df_this.shape[0]
  if tq is not None: tq.close()
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")
  return df

#############################################################################
def ListMolecules(dev_phase, skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  '''Ignore synonyms here.'''
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/molecule.json?limit={NCHUNK}"
  if skip: url_next += f"&offset={skip}"
  if dev_phase: url_next += f"&max_phase={dev_phase}"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    mols = result["molecules"] if "molecules" in result else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not mol_tags:
        mol_tags = [tag for tag in sorted(list(mol.keys())) if type(mol[tag]) not in (dict, list)]
      if not struct_tags:
        struct_tags = sorted(mol["molecule_structures"].keys())
        struct_tags.remove("molfile")
      if not prop_tags:
        prop_tags = sorted(mol["molecule_properties"].keys())
      parent_chembl_id = mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and "parent_chembl_id" in mol["molecule_hierarchy"] else ""
      df_this = pd.concat([
	pd.DataFrame({tag:[(mol[tag] if tag in mol else None)] for tag in mol_tags}),
	pd.DataFrame({tag:[(mol["molecule_structures"][tag] if tag in mol["molecule_structures"] else None)] for tag in struct_tags}),
	pd.DataFrame({tag:[(mol["molecule_properties"][tag] if tag in mol["molecule_properties"] else None)] for tag in prop_tags}),
	pd.DataFrame({"parent_chembl_id":[parent_chembl_id]})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="mols")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListDrugs(skip, nmax, api_host=API_HOST, api_base_path=API_BASE_PATH, fout=None):
  n_mol=0; n_out=0; n_err=0; tags=None; struct_tags=None; prop_tags=None; df=None; tq=None;
  url_next = f"{api_base_path}/drug.json?limit={NCHUNK}&offset={skip}"
  while True:
    response = requests.get(f"https://{api_host}{url_next}")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      break
    result = response.json()
    mols = result["drugs"] if "drugs" in result else []
    for mol in mols:
      n_mol+=1
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      if not mol_tags:
        mol_tags = [tag for tag in sorted(list(mol.keys())) if type(mol[tag]) not in (dict, list)]
      if not struct_tags:
        struct_tags = sorted(mol["molecule_structures"].keys())
        struct_tags.remove("molfile")
      if not prop_tags:
        prop_tags = sorted(mol["molecule_properties"].keys())
      parent_chembl_id = mol["molecule_hierarchy"]["parent_chembl_id"] if "molecule_hierarchy" in mol and "parent_chembl_id" in mol["molecule_hierarchy"] else ""
      df_this = pd.concat([
	pd.DataFrame({tag:[(mol[tag] if tag in mol else None)] for tag in mol_tags}),
	pd.DataFrame({tag:[(mol["molecule_structures"][tag] if tag in mol["molecule_structures"] else None)] for tag in struct_tags}),
	pd.DataFrame({tag:[(mol["molecule_properties"][tag] if tag in mol["molecule_properties"] else None)] for tag in prop_tags}),
	pd.DataFrame({"parent_chembl_id":[parent_chembl_id]})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
      if tq is not None: tq.update()
      if nmax and n_mol>=nmax: break
    if nmax and n_mol>=nmax: break
    total_count = result["page_meta"]["total_count"] if "page_meta" in result and "total_count" in result["page_meta"] else None
    if not tq: tq = tqdm.tqdm(total=total_count, unit="drugs")
    url_next = result["page_meta"]["next"] if "page_meta" in result and "next" in result["page_meta"] else None
    if not url_next: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def SearchMoleculeByName(ids, base_url=BASE_URL, fout=None):
  """IDs should be names/synonyms."""
  n_out=0; n_notfound=0; df=None; synonym_tags=None;
  tags = ["molecule_chembl_id"]
  for id_this in ids:
    response = requests.get(f"{base_url}/molecule/search?q={urllib.parse.quote(id_this)}", headers={"Accept":"application/json"})
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      n_notfound+=1
      continue
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    mols = result["molecules"] if "molecules" in result else []
    for mol in mols:
      logging.debug(json.dumps(mol, sort_keys=True, indent=2))
      synonyms = mol["molecule_synonyms"] if "molecule_synonyms" in mol else []
      for synonym in synonyms:
        if not synonym_tags:
          synonym_tags = list(synonym.keys())
        molecule_synonym = synonym["molecule_synonym"] if "molecule_synonym" in synonym else ""
        if not re.search(id_this, molecule_synonym, re.I):
          continue
        molecule_chembl_id = mol["molecule_chembl_id"] if "molecule_chembl_id" in mol else ""
      df_this = pd.concat([
	pd.DataFrame({"molecule_chembl_id":[molecule_chembl_id]}),
	pd.DataFrame({tag:[(synonum[tag] if tag in synonum else None)] for tag in synonym_tags})], axis=1)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=df_this.shape[0]
  logging.info(f"n_in: {len(ids)}; n_found: {len(ids)-n_notfound}; n_out: {n_out}")
  return df

#############################################################################
def GetMoleculeByInchikey(ids, base_url=BASE_URL, fout=None):
  """Requires InChI key, e.g. "GHBOEFUAGSHXPO-XZOTUCIWSA-N"."""
  n_out=0; tags=[]; struct_tags=[]; df=None; tq=None;
  for id_this in ids:
    if not tq: tq = tqdm.tqdm(total=len(ids), unit="mols")
    tq.update()
    response = requests.get(f"{base_url}/molecule/{id_this}.json")
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    mol = response.json()
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
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out+=df_this.shape[0]
  if tq is not None: tq.close()
  logging.info(f"n_qry: {len(ids)}; n_out: {n_out}; n_not_found: {len(ids)-n_out}")
  return df

#############################################################################
