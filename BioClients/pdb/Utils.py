#!/usr/bin/env python3
##############################################################################
### pdb_utils.py - utility functions for PDB REST API.
### 
### See: http://www.rcsb.org/pdb/software/rest.do
### 
### API supports CSV output.  So we could use this directly.
##############################################################################
### Ligand types:
### "D-beta-peptide, C-gamma linking",	20,0.010%
### "D-gamma-peptide, C-delta linking",	39,0.019%
### "D-peptide NH3 amino terminus",	1,0.000%
### "D-peptide linking",		1222,0.588%
### "D-saccharide",			10329,4.967%
### "D-saccharide 1, 4 and 1, 4 linking",	39,0.019%
### "DNA OH 3 prime terminus",		20,0.010%
### "DNA linking",			1847,0.888%
### "L-DNA linking",			5,0.002%
### "L-RNA linking",			21,0.010%
### "L-beta-peptide, C-gamma linking",	44,0.021%
### "L-gamma-peptide, C-delta linking",	9,0.004%
### "L-peptide COOH carboxy terminus",	51,0.025%
### "L-peptide NH3 amino terminus",	24,0.012%
### "L-peptide linking",		18676,8.981%
### "L-saccharide",			291,0.140%
### "L-saccharide 1, 4 and 1, 4 linking",	2,0.001%
### "RNA OH 3 prime terminus",		8,0.004%
### "RNA linking",			3538,1.701%
### "non-polymer",			166510,80.074%
### "peptide linking",			296,0.142%
### "peptide-like",			1035,0.498%
### "saccharide",			3914,1.882%
##############################################################################
import sys,os,re,time,logging
#
from xml.etree import ElementTree
#
import rdkit.Chem
#
from ..util import rest_utils
from ..util import xml_utils
#
REST_RETRY_NMAX=10
REST_RETRY_WAIT=5
#
#############################################################################
def GetProteinData(base_url, pid):
  url=base_url+'/describePDB?structureId=%s'%pid
  logging.debug(url)
  try:
    etree=rest_utils.GetURL(url, parse_xml=True)
  except Exception as e:
    logging.debug('%s'%(e))
  data=[];
  proteins = etree.findall('/PDBdescription/PDB')
  for protein in proteins:
    p={};
    for i in range(protein.attributes.length):
      attr = protein.attributes.item(i)
      p[attr.name]=attr.value
    data.append(p)
  return data

#############################################################################
def GetProteins(base_url, pids, fout):
  n_out=0; tags=[];
  for pid in pids:
    data=GetProteinData(base_url, pid)
    for p in data:
      if n_out==0:
        tags=sorted(p.keys())
        fout.write('\t'.join(tags)+'\n')
      vals=[(p[tag] if p.has_key(tag) else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  logging.info('queries: %d ; proteins out: %d'%(len(pids), n_out))

#############################################################################
def GetLigandData(base_url, pid):
  data=[];
  url=base_url+'/ligandInfo?structureId=%s'%pid
  logging.debug(url)
  try:
    etree=rest_utils.GetURL(url, parse_xml=True)
    ligands = etree.findall('/structureId/ligandInfo/ligand')
  except Exception as e:
    logging.debug('%s'%(e))
    return data
  #logging.debug('%s'%dom.toprettyxml())
  for ligand in ligands:
    lig={};
    for i in range(ligand.attributes.length):
      attr = ligand.attributes.item(i)
      lig[attr.name]=attr.value
    for cnode in ligand.childNodes:
      if cnode.nodeName =='#text': continue
      lig[cnode.nodeName]=xml_utils.DOM_NodeText(cnode)
    data.append(lig)
  return data

#############################################################################
def GetLigands(base_url, pids, druglike, fout):
  n_all=0; n_out=0; n_rejected=0; tags=[];
  for pid in pids:
    data=GetLigandData(base_url, pid)
    for d in data:
      n_all+=1
      if druglike and not LigandIsDruglike(d):
        n_rejected+=1
        continue
      if n_out==0:
        tags=sorted(d.keys())
        fout.write('\t'.join(['pdbid']+tags)+'\n')
      vals=[(d[tag] if d.has_key(tag) else '') for tag in tags]
      vals = map(lambda s:s.replace('"', '&quot;'), vals) #escape quotes
      fout.write('\t'.join([pid]+vals)+'\n')
      n_out+=1
  logging.info('queries: %d ; ligands: %d ; ligands out: %d ; rejected: %d'%(len(pids), n_all, n_out, n_rejected))

#############################################################################
def LigandIsDruglike(lig):
  '''Very simple criteria to exclude monoatomic, polymers, etc.'''
  if not lig: return False
  if type(lig) != types.DictType: return False
  ligtype = lig['type'] if lig.has_key('type') else None
  mf = lig['formula'] if lig.has_key('formula') else None
  mwt = float(lig['molecularWeight']) if lig.has_key('molecularWeight') else None
  smi = lig['smiles'] if lig.has_key('smiles') else None
  if not smi: return False
  if ligtype != 'non-polymer': return False
  if not mwt or mwt < 100.0 or mwt > 1000.0: return False
  if len(re.sub(r'[^A-Z]', '', smi))<6: return False  #Cheap approx atomcount
  try:
    mol=rdkit.Chem.MolFromSmiles(smi)
    if mol and mol.GetNumAtoms()<8: return False
  except Exception as e:
    logging.debug("ERROR: smi = \"%s\" (%s)"%(smi, str(e)))
    return False
  return True

#############################################################################
def GetUniprotData(base_url, pid):
  '''Former bug semi? fixed May 2015.  Now works for awhile then freezes.'''
  url=base_url+'/das/pdb_uniprot_mapping/alignment?query=%s'%pid
  try:
    etree=rest_utils.GetURL(url, parse_xml=True)
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
  '''Using first record to define tags; not very reliable.'''
  n_out=0; tags=[];
  for pid in pids:
    data=GetUniprotData(base_url, pid)
    for d in data:
      if n_out==0:
        tags=sorted(d.keys())
        fout.write('\t'.join(['queryId']+tags)+'\n')
        logging.debug('tags = %s'%str(tags))
      vals=[(d[tag] if d.has_key(tag) else '') for tag in tags]
      fout.write('\t'.join([pid]+vals)+'\n')
      fout.flush()
      n_out+=1
  logging.info('queries: %d ; uniprots out: %d'%(len(pids), n_out))

#############################################################################
def AllProteins(base_url, fout):
  try:
    etree=rest_utils.GetURL(base_url+'/getCurrent', parse_xml=True)
  except Exception as e:
    logging.error('%s'%(e))
  proteins = etree.findall('/current/PDB')
  pids=[]
  for protein in proteins:
    pid=protein.getAttribute('structureId')
    pids.append(pid)
  return pids

#############################################################################
def ListProteins(base_url, fout):
  pids=AllProteins(base_url, fout)
  GetProteins(base_url, pids, fout)

#############################################################################
def ListLigands(base_url, druglike, fout):
  pids=AllProteins(base_url, fout)
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
    txt=rest_utils.PostURL(base_url+'/search', data=query_xml, parse_xml=False)
  except Exception as e:
    logging.error('%s'%(e))
  pids=[]
  for pid in txt.splitlines():
    if pid: pids.append(pid)
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
      txt=rest_utils.PostURL(base_url+'/search', data=query_xml, parse_xml=False)
    except Exception as e:
      logging.error('%s'%(e))
    pids=[]
    for pid in txt.splitlines():
      if pid: pids.append(pid)

    n_out=0;
    #tags=[];
    for pid in pids:
      data=GetProteinData(base_url, pid)
      for p in data:
        #if n_out==0:
        #  tags=sorted(p.keys())
        #  fout.write('\t'.join(['uniprot']+tags)+'\n')
        vals=[(p[tag] if p.has_key(tag) else '') for tag in tags]
        fout.write('\t'.join([uniprot]+vals)+'\n')
        n_out+=1
    logging.info('query: %s ; pdbids: %d ; out: %d'%(uniprot, len(pids), n_out))
    n_out_total+=n_out;
    n_pids_total+=len(pids)
  logging.info('Total queries: %d ; pdbids: %d ; out: %d'%(len(uniprots), n_pids_total, n_out_total))

#############################################################################
