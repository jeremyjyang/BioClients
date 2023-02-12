#!/usr/bin/env python3
"""
Utility functions for PDB REST API.
https://www.rcsb.org/docs/programmatic-access/web-services-overview
https://data.rcsb.org/redoc/

Major changes include all JSON output.
"""
###
import sys,os,re,time,logging,requests
#
import rdkit.Chem
#
API_HOST='data.rcsb.org'
API_BASE_PATH='/rest/v1/core'
#
#############################################################################
def GetProteinData(pid, base_url):
  """E.g. https://data.rcsb.org/rest/v1/core/entry/3ert"""
  url = f"{base_url}/entry/{pid}"
  logging.debug(url)
  response = requests.get(url)
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  logging.debug(response.content)
  result = response.json()

  # Fix and update to new JSON and schema.
  proteins = etree.findall('./PDB')
  logging.debug(f"Proteins found: {len(proteins)}")
  data = [protein.attrib for protein in proteins]
  return data

#############################################################################
def GetProteins(pids, base_url, fout):
  n_out=0; tags=[];
  for pid in pids:
    data = GetProteinData(pid, base_url)
    for p in data:
      if n_out==0:
        tags = sorted(p.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(p[tag] if tag in p else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  logging.info(f"queries: {len(pids)}; proteins out: {n_out}")

#############################################################################
def GetLigandData(pid, base_url):
  url = (f"{base_url}/ligandInfo?structureId={pid}")
  logging.debug(url)
  response = requests.get(url)
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  etree = ElementTree.fromstring(response.content)
  #ligands = etree.findall('/structureId/ligandInfo/ligand')
  ligands = etree.findall('./ligandInfo/ligand')
  data=[];
  for ligand in ligands:
    ligdata = ligand.attrib
    for cnode in ligand.iter():
      ligdata[cnode.tag] = cnode.text
    data.append(ligdata)
  return data

#############################################################################
def GetLigands(pids, druglike, base_url, fout):
  n_all=0; n_out=0; n_rejected=0; tags=[];
  for pid in pids:
    data = GetLigandData(base_url, pid)
    for d in data:
      n_all+=1
      if druglike and not LigandIsDruglike(d):
        n_rejected+=1
        continue
      if n_out==0:
        tags = sorted(d.keys())
        fout.write('\t'.join(['pdbid']+tags)+'\n')
      vals = [(d[tag] if tag in d else '') for tag in tags]
      fout.write('\t'.join([pid]+vals)+'\n')
      n_out+=1
  logging.info(f"queries: {len(pids)}; ligands: {n_all}; ligands out: {n_out}; rejected: {n_rejected}")

#############################################################################
def GetLigands_LID2SDF(lids, base_url, fout):
  """Note that each LID many SDFs, one for each occurance. Note also
  base_url arg ignored in this function. May be hacky and unsupported API
  functionality."""
  logging.info(f"LIDs: {len(lids)}")
  n_lid=0; n_sdf=0; n_lid2sdf=0; n_notfound=0; n_err=0;
  for lid in lids:
    n_lid+=1
    url = (f"https://www.rcsb.org/pdb/download/downloadLigandFiles.do?ligandIdList={lid}")
    logging.debug(url)
    response = requests.get(url)
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
      continue
    rval = response.content
    if type(rval) is not str:
      logging.error(f"type(RVAL) NOT STR ({url}), type={type(rval)}: {rval}")
    elif re.search(r'^<!DOCTYPE html>.*No files found', rval, re.DOTALL|re.I):
      n_notfound+=1
    elif re.search(r'^<!DOCTYPE html>', rval, re.I):
      n_err+=1
      logging.error(f"RVAL NOT SDF ({url}): {rval}")
    else:
      fout.write(rval)
      n_sdf_this = len(re.findall(r'\$\$\$\$[\r\n]', rval))
      if n_sdf_this>0: n_lid2sdf+=1
      n_sdf+=n_sdf_this
    if n_lid%1000==0:
      logging.info(f"LIDs: {n_lid}; LID2SDF: {n_lid2sdf}; not_found: {n_notfound}; SDFs out: {n_sdf}")
  logging.info(f"LIDs: {n_lid}; LID2SDF: {n_lid2sdf}; not_found: {n_notfound}; SDFs out: {n_sdf}")

#############################################################################
def LigandIsDruglike(lig):
  '''Very simple criteria to exclude monoatomic, polymers, etc.'''
  if not lig: return False
  if type(lig) != types.DictType: return False
  ligtype = lig['type'] if 'type' in lig else None
  mf = lig['formula'] if 'formula' in lig else None
  mwt = float(lig['molecularWeight']) if 'molecularWeight' in lig else None
  smi = lig['smiles'] if 'smiles' in lig else None
  if not smi: return False
  if ligtype != 'non-polymer': return False
  if not mwt or mwt < 100.0 or mwt > 1000.0: return False
  if len(re.sub(r'[^A-Z]', '', smi))<6: return False  #Cheap approx atomcount
  try:
    mol = rdkit.Chem.MolFromSmiles(smi)
    if mol and mol.GetNumAtoms()<8: return False
  except Exception as e:
    logging.error(f"smi = \"{smi}\" ({e})")
    return False
  return True

#############################################################################
def GetUniprotData(pid, base_url):
  '''API functionality maybe discontinued.'''
  url = f"{base_url}/das/pdb_uniprot_mapping/alignment?query={pid}"
  response = requests.get(url)
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  etree = ElementTree.fromstring(response.content)
  data=[]; al={};
  alignments = etree.findall('/dasalignment/alignment/alignObject')
  for alignment in alignments:
    if util_xml.DOM_GetNodeAttr(alignment, 'dbSource')=='UniProt':
      for i in range(alignment.attributes.length):
        attr = alignment.attributes.item(i)
        al[attr.name]=attr.value
    #for cnode in alignment.childNodes:
    #  if cnode.nodeName =='#text': continue
    #  al[cnode.nodeName]=util_xml.DOM_NodeText(cnode)
    data.append(al)
  return data

#############################################################################
def GetUniprots(pids, base_url, fout):
  n_out=0; tags=[];
  for pid in pids:
    data=GetUniprotData(pid, base_url)
    for d in data:
      if n_out==0:
        tags=sorted(d.keys())
        fout.write('\t'.join(['queryId']+tags)+'\n')
        logging.debug(f"tags = {str(tags)}")
      vals=[(d[tag] if tag in d else '') for tag in tags]
      fout.write('\t'.join([pid]+vals)+'\n')
      fout.flush()
      n_out+=1
  logging.info(f"queries: {len(pids)}; uniprots out: {n_out}")

#############################################################################
def AllPIDs(base_url):
  response = requests.get(base_url+'/getCurrent')
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  results = response.json()
  pids = results['idList']
  return pids

#############################################################################
def ShowCounts(base_url):
  pids = AllPIDs(base_url)
  logging.info(f"IDs: {len(pids)}")

#############################################################################
def ListProteins(base_url, fout):
  pids = AllPIDs(base_url)
  logging.info(f"IDs: {len(pids)}")
  GetProteins(pids, base_url, fout)

#############################################################################
def ListLigands(druglike, base_url, fout):
  pids = AllPIDs(base_url)
  logging.info(f"IDs: {len(pids)}")
  GetLigands(pids, druglike, base_url, fout)

#############################################################################
def SearchByKeywords(kwds, base_url):
  query_xml = f'''\
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<queryType>org.pdb.query.simple.AdvancedKeywordQuery</queryType>
<description>Text Search for: "{','.join(kwds)}"</description>
<keywords>{','.join(kwds)}</keywords>
</orgPdbQuery>
'''
  response = requests.post(f"{base_url}/search", data=query_xml)
  if response.status_code != 200:
    logging.error(f"status_code: {response.status_code}")
    return []
  txt = response.content
  pids = [pid.strip() for pid in txt.splitlines()]
  return pids

#############################################################################
def SearchByUniprot(uniprots, base_url, fout):
  n_out_total=0; n_pids_total=0;
  tags=["structureId", "title", "expMethod", "keywords", "pubmedId", "resolution", "status"]
  fout.write('\t'.join(['uniprot']+tags)+'\n')

  for uniprot in uniprots:
    query_xml = f'''\
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<queryType>org.pdb.query.simple.UpAccessionIdQuery</queryType>
<description>Simple query for a list of Uniprot Accession ID: "{uniprot}"</description>
<accessionIdList>{uniprot}</accessionIdList>
</orgPdbQuery>
'''
    response = requests.post(base_url+'/search', data=query_xml)
    if response.status_code != 200:
      logging.error(f"status_code: {response.status_code}")
    txt = response.content
    pids=[]
    for pid in txt.splitlines():
      if pid: pids.append(pid)
    n_out=0;
    for pid in pids:
      data = GetProteinData(pid, base_url)
      for p in data:
        vals=[(p[tag] if tag in p else '') for tag in tags]
        fout.write('\t'.join([uniprot]+vals)+'\n')
        n_out+=1
    logging.info(f"query: {uniprot}; pdbids: {len(pids)}; out: {n_out}")
    n_out_total+=n_out;
    n_pids_total+=len(pids)
  logging.info(f"Total queries: {len(uniprots)}; pdbids: {n_pids_total}; out: {n_out_total}")

#############################################################################
