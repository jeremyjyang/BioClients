#!/usr/bin/env python3
"""
Utility functions for PDB REST API.
https://www.rcsb.org/docs/programmatic-access/web-services-overview
https://data.rcsb.org/redoc/

Major changes include all JSON output.
"""
###
import sys,os,re,time,json,logging,requests
#
API_HOST='data.rcsb.org'
API_BASE_PATH='/rest/v1'
API_BASE_URL = f"https://{API_HOST}{API_BASE_PATH}"
#
#############################################################################
def GetEntryData(eid, base_url=API_BASE_URL):
  """E.g. https://data.rcsb.org/rest/v1/core/entry/3ert"""
  response = requests.get(f"{base_url}/core/entry/{eid}")
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return None
  logging.debug(response.content)
  result = response.json()
  return result

#############################################################################
def GetEntrys(eids, base_url=API_BASE_URL, fout=None):
  n_out=0; tags=[];
  for eid in eids:
    result = GetEntryData(eid, base_url)
    fout.write(json.dumps(result, indent=2)+"\n")
    n_out+=1
  logging.info(f"queries: {len(eids)}; entrys out: {n_out}")

#############################################################################
def GetChemicalData(cid, base_url):
  """Chemical component (ligands, small molecules and monomers) via CCD ID. E.g. https://data.rcsb.org/rest/v1/core/chemcomp/CFF"""
  response = requests.get(f"{base_url}/core/chemcomp/{cid}")
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return None
  logging.debug(response.content)
  result = response.json()
  return result

#############################################################################
def GetChemicals(cids, druglike, base_url=API_BASE_URL, fout=None):
  n_all=0; n_out=0; n_rejected=0; tags=[];
  for cid in cids:
    result = GetChemicalData(base_url, cid)
    if result is None:
      continue
    n_all+=1
    if druglike and not ChemicalIsDruglike(result):
      n_rejected+=1
      continue
    fout.write(result)
    n_out+=1
  logging.info(f"queries: {len(cids)}; chemicals: {n_all}; chemicals out: {n_out}; rejected: {n_rejected}")

#############################################################################
def ChemicalIsDruglike(chem):
  '''Simple criteria to exclude monoatomic, polymers, etc.'''
  chem_comp = chem['chem_comp'] if 'chem_comp' in chem else None
  if not chem_comp: return False
  chemtype = chem_comp['type'] if 'type' in chem_comp else None
  if chemtype != 'non-polymer': return False
  mf = chem_comp['formula'] if 'formula' in chem_comp else None
  formula_weight = chem_comp['formula_weight'] if 'formula_weight' in chem_comp else None
  if not formula_weight or formula_weight<100 or formula_weight>1000: return False
  rcsb_chem_comp_descriptor = chem['rcsb_chem_comp_descriptor'] if 'rcsb_chem_comp_descriptor' in chem else None
  smi = rcsb_chem_comp_descriptor['smiles'] if 'smiles' in rcsb_chem_comp_descriptor else None
  if not smi: return False
  rcsb_chem_comp_info = chem['rcsb_chem_comp_info'] if 'rcsb_chem_comp_info' in chem else None
  atom_count = rcsb_chem_comp_info['atom_count'] if 'atom_count' in rcsb_chem_comp_info else None
  if atom_count<6: return False
  return True

#############################################################################
def ListEntrys(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/holdings/current/entry_ids")
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  results = response.json()
  if fout is not None:
    for eid in results:
      fout.write(f"{eid}\n")
  logging.info(f"Entrys: {len(results)}")
  return results

#############################################################################
#############################################################################
