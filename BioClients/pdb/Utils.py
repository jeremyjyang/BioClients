#!/usr/bin/env python3
"""
Utility functions for PDB REST API.
See: http://www.rcsb.org/pdb/software/rest.do
API supports CSV output.  So we could use this directly.

Ligand types:
    "D-beta-peptide, C-gamma linking",	20,0.010%
    "D-gamma-peptide, C-delta linking",	39,0.019%
    "D-peptide NH3 amino terminus",	1,0.000%
    "D-peptide linking",		1222,0.588%
    "D-saccharide",			10329,4.967%
    "D-saccharide 1, 4 and 1, 4 linking",	39,0.019%
    "DNA OH 3 prime terminus",		20,0.010%
    "DNA linking",			1847,0.888%
    "L-DNA linking",			5,0.002%
    "L-RNA linking",			21,0.010%
    "L-beta-peptide, C-gamma linking",	44,0.021%
    "L-gamma-peptide, C-delta linking",	9,0.004%
    "L-peptide COOH carboxy terminus",	51,0.025%
    "L-peptide NH3 amino terminus",	24,0.012%
    "L-peptide linking",		18676,8.981%
    "L-saccharide",			291,0.140%
    "L-saccharide 1, 4 and 1, 4 linking",	2,0.001%
    "RNA OH 3 prime terminus",		8,0.004%
    "RNA linking",			3538,1.701%
    "non-polymer",			166510,80.074%
    "peptide linking",			296,0.142%
    "peptide-like",			1035,0.498%
    "saccharide",			3914,1.882%
"""
###
import sys,os,re,time,logging
#
from xml.etree import ElementTree
#
import rdkit.Chem
#
from ..util import rest
from ..util import xml_utils
#
#############################################################################
def GetProteinData(base_url, pid):
  url = (base_url+'/describePDB?structureId=%s'%pid)
  logging.debug(url)
  try:
    etree = rest.GetURL(url, parse_xml=True)
  except Exception as e:
    logging.error('%s'%(e))
    return []
  #proteins = etree.findall('/PDBdescription/PDB')
  proteins = etree.findall('./PDB')
  logging.debug("Proteins found: %d"%len(proteins))
  data = [protein.attrib for protein in proteins]
  return data

#############################################################################
def GetProteins(base_url, pids, fout):
  n_out=0; tags=[];
  for pid in pids:
    data = GetProteinData(base_url, pid)
    for p in data:
      if n_out==0:
        tags = sorted(p.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(p[tag] if tag in p else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  logging.info('queries: %d ; proteins out: %d'%(len(pids), n_out))

#############################################################################
def GetLigandData(base_url, pid):
  url = (base_url+'/ligandInfo?structureId=%s'%pid)
  logging.debug(url)
  try:
    etree = rest.GetURL(url, parse_xml=True)
    #ligands = etree.findall('/structureId/ligandInfo/ligand')
    ligands = etree.findall('./ligandInfo/ligand')
  except Exception as e:
    logging.debug('%s'%(e))
    return []
  data=[];
  for ligand in ligands:
    ligdata = ligand.attrib
    for cnode in ligand.iter():
      ligdata[cnode.tag] = cnode.text
    data.append(ligdata)
  return data

#############################################################################
def GetLigands(base_url, pids, druglike, fout):
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
  logging.info('queries: %d ; ligands: %d ; ligands out: %d ; rejected: %d'%(len(pids), n_all, n_out, n_rejected))

#############################################################################
def GetLigands_LID2SDF(base_url, lids, fout):
  """Note that each LID many SDFs, one for each occurance. Note also
  base_url arg ignored in this function. May be hacky and unsupported API
  functionality."""
  logging.info('LIDs: %d'%len(lids))
  n_lid=0; n_sdf=0; n_lid2sdf=0; n_notfound=0; n_err=0;
  for lid in lids:
    n_lid+=1
    url = ('https://www.rcsb.org/pdb/download/downloadLigandFiles.do?ligandIdList=%s'%lid)
    logging.debug(url)
    try:
      rval = rest.GetURL(url, parse_json=False)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    if type(rval) is not str:
      logging.error('ERROR: type(RVAL) NOT STR (%s).'%(url))
      logging.debug('ERROR: type(RVAL) NOT STR (%s), type=%s:\n%s'%(url,type(rval),str(rval)))
    elif re.search(r'^<!DOCTYPE html>.*No files found', rval, re.DOTALL|re.I):
      n_notfound+=1
    elif re.search(r'^<!DOCTYPE html>', rval, re.I):
      n_err+=1
      logging.error('ERROR: RVAL NOT SDF (%s).'%(url))
      logging.debug('ERROR: RVAL NOT SDF (%s):\n%s'%(url,rval))
    else:
      fout.write(rval)
      n_sdf_this = len(re.findall(r'\$\$\$\$[\r\n]', rval))
      if n_sdf_this>0: n_lid2sdf+=1
      n_sdf+=n_sdf_this
    if n_lid%1000==0:
      logging.info('LIDs: %d; LID2SDF: %d; not_found: %d; SDFs out: %d'%(n_lid, n_lid2sdf, n_notfound, n_sdf))
  logging.info('LIDs: %d; LID2SDF: %d; not_found: %d; SDFs out: %d'%(n_lid, n_lid2sdf, n_notfound, n_sdf)) 

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
    logging.error("smi = \"%s\" (%s)"%(smi, str(e)))
    return False
  return True

#############################################################################
def GetUniprotData(base_url, pid):
  '''API functionality maybe discontinued.'''
  url = base_url+'/das/pdb_uniprot_mapping/alignment?query=%s'%pid
  try:
    etree = rest.GetURL(url, parse_xml=True)
  except Exception as e:
    logging.debug('%s'%(e))
  if not etree:
    return []
  #logging.debug('%s'%dom.toprettyxml())
  data=[];
  al={}
  alignments = etree.findall('/dasalignment/alignment/alignObject')
  for alignment in alignments:
    if xml_utils.DOM_GetNodeAttr(alignment, 'dbSource')=='UniProt':
      for i in range(alignment.attributes.length):
        attr = alignment.attributes.item(i)
        al[attr.name]=attr.value
    #for cnode in alignment.childNodes:
    #  if cnode.nodeName =='#text': continue
    #  al[cnode.nodeName]=xml_utils.DOM_NodeText(cnode)
    data.append(al)
  return data

#############################################################################
def GetUniprots(base_url, pids, fout):
  n_out=0; tags=[];
  for pid in pids:
    data=GetUniprotData(base_url, pid)
    for d in data:
      if n_out==0:
        tags=sorted(d.keys())
        fout.write('\t'.join(['queryId']+tags)+'\n')
        logging.debug('tags = %s'%str(tags))
      vals=[(d[tag] if tag in d else '') for tag in tags]
      fout.write('\t'.join([pid]+vals)+'\n')
      fout.flush()
      n_out+=1
  logging.info('queries: %d ; uniprots out: %d'%(len(pids), n_out))

#############################################################################
#def AllPIDs(base_url):
#  try:
#    etree = rest.GetURL(base_url+'/getCurrent', parse_xml=True)
#  except Exception as e:
#    logging.error('%s'%(e))
#    return []
#  #proteins = etree.findall('/current/PDB')
#  proteins = etree.findall('./PDB')
#  pids = [protein.get('structureId') for protein in proteins]
#  return pids
#
#############################################################################
def AllPIDs(base_url):
  try:
    rval = rest.GetURL(base_url+'/getCurrent', parse_json=True)
  except Exception as e:
    logging.error('HTTP Error: %s'%(e))
    return []
  pids = rval['idList']
  return pids

#############################################################################
def ShowCounts(base_url):
  pids = AllPIDs(base_url)
  logging.info("IDs: %d"%(len(pids)))

#############################################################################
def ListProteins(base_url, fout):
  pids = AllPIDs(base_url)
  logging.info("IDs: %d"%(len(pids)))
  GetProteins(base_url, pids, fout)

#############################################################################
def ListLigands(base_url, druglike, fout):
  pids = AllPIDs(base_url)
  logging.info("IDs: %d"%(len(pids)))
  GetLigands(base_url, pids, druglike, fout)

#############################################################################
def SearchByKeywords(base_url, kwds):
  query_xml='''\
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<queryType>org.pdb.query.simple.AdvancedKeywordQuery</queryType>
<description>Text Search for: "%(KWDS)s"</description>
<keywords>%(KWDS)s</keywords>
</orgPdbQuery>
'''%{'KWDS':(','.join(kwds))}
  try:
    txt = rest.PostURL(base_url+'/search', data=query_xml, parse_xml=False)
  except Exception as e:
    logging.error('%s'%(e))
    return []
  pids = [pid.strip() for pid in txt.splitlines()]
  return pids

#############################################################################
def SearchByUniprot(base_url, uniprots, fout):
  n_out_total=0; n_pids_total=0;
  tags=["structureId", "title", "expMethod", "keywords", "pubmedId", "resolution", "status"]
  fout.write('\t'.join(['uniprot']+tags)+'\n')

  for uniprot in uniprots:
    query_xml='''\
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<queryType>org.pdb.query.simple.UpAccessionIdQuery</queryType>
<description>Simple query for a list of Uniprot Accession ID: "%(UNIPROT)s"</description>
<accessionIdList>%(UNIPROT)s</accessionIdList>
</orgPdbQuery>
'''%{'UNIPROT':uniprot}
    try:
      txt=rest.PostURL(base_url+'/search', data=query_xml, parse_xml=False)
    except Exception as e:
      logging.error('%s'%(e))
    pids=[]
    for pid in txt.splitlines():
      if pid: pids.append(pid)

    n_out=0;
    #tags=[];
    for pid in pids:
      data = GetProteinData(base_url, pid)
      for p in data:
        #if n_out==0:
        #  tags=sorted(p.keys())
        #  fout.write('\t'.join(['uniprot']+tags)+'\n')
        vals=[(p[tag] if tag in p else '') for tag in tags]
        fout.write('\t'.join([uniprot]+vals)+'\n')
        n_out+=1
    logging.info('query: %s ; pdbids: %d ; out: %d'%(uniprot, len(pids), n_out))
    n_out_total+=n_out;
    n_pids_total+=len(pids)
  logging.info('Total queries: %d ; pdbids: %d ; out: %d'%(len(uniprots), n_pids_total, n_out_total))

#############################################################################
