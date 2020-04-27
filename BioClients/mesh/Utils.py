#!/usr/bin/env python3
"""
MeSH XML utility functions.

MeSH XML
Download: https://www.nlm.nih.gov/mesh/download_mesh.html
Doc: https://www.nlm.nih.gov/mesh/xml_data_elements.html
"""
###
import sys,os,re,logging
import xml.etree.cElementTree as ElementTree
from xml.parsers import expat

#############################################################################
def Desc2Csv(branch, fin, fout):
  fout.write('id\ttreenum\tterm\n')
  n_elem=0; n_term=0;
  for event, elem in ElementTree.iterparse(fin):
    meshid,meshterm,desclass,treenum = None,None,None,None;
    n_elem+=1
    logging.debug('Event:%6s, elem.tag:%6s, elem.text:"%6s"'%(event,elem.tag,elem.text.strip() if elem.text else ''))
    if elem.tag == 'DescriptorRecord':
      if elem.attrib['DescriptorClass'] != '1': continue
      meshid,meshterm,desclass,treenum = None,None,None,None;
      meshid=elem.findtext('DescriptorUI')
      #treenum=elem.findtext('TreeNumberList/TreeNumber')
      elems = elem.findall('TreeNumberList/TreeNumber')
      treenums = map(lambda e: e.text, elems)
      for treenum in treenums:
        if (re.match(r'^%s'%branch,treenum)): break
      meshterm=elem.findtext('DescriptorName/String')
      #See also: ConceptList/Concept/TermList/Term/String (may be multiple)

      if not meshid:
        logging.info('skipping, no meshid: %s'%str(elem))
      elif not meshterm:
        logging.info('meshid: %s ; skipping, no meshterm'%meshid)
      elif not treenum:
        logging.info('meshid: %s ; skipping, no treenum'%meshid)
      elif not re.match(r'^%s'%branch,treenum):
        logging.info('meshid: %s ; skipping, non-%s treenum: %s'%(meshid,branch,treenum))
      else:
        fout.write('%s\t%s\t%s\n'%(meshid,treenum,meshterm))
        n_term+=1

  logging.info('DEBUG: n_elem: %d'%n_elem)
  logging.info('DEBUG: n_term: %d'%n_term)

#############################################################################
### SCRClass
### Description: Attribute of <DescriptorRecord> one of:
### 1 = Regular chemical, drug, or other substance (the most common type)
### 2 = Protocol, for example, FOLFOXIRI protocol
### 3 = Rare disease, for example, Canicola fever
### Subelement of: not applicable. Attribute of <SupplementalRecord>
### Record Type: SCR
### https://www.nlm.nih.gov/mesh/xml_data_elements.html
#############################################################################
### There are non-disease records mapped to diseases, e.g. C041229,
### "GHM protein, human", SCRClass=1, is mapped to D006362, "Heavy Chain Disease".
### These cannot be identified from the supplementary file alone.
#############################################################################
def Supp2Csv(branch, fin, fout):
  fout.write('id\tterm\tid_to\tterm_to\n')
  n_elem=0; n_term=0;
  for event,elem in ElementTree.iterparse(fin):
    meshid,name,meshid_to,meshterm_to = None,None,None,None;
    n_elem+=1
    logging.debug('Event:%6s, elem.tag:%6s, elem.text:"%6s"'%(event,elem.tag,elem.text.strip() if elem.text else ''))
    if elem.tag == 'SupplementalRecord':
      scrclass = elem.attrib['SCRClass']
      if branch not in ('C', 'D'): continue
      if branch=='C' and scrclass!='3': continue #disease-only
      if branch=='D' and scrclass!='1': continue #chemical-only
      meshid=elem.findtext('SupplementalRecordUI')
      name=elem.findtext('SupplementalRecordName/String')
      mtlist=elem.find('HeadingMappedToList')
      if mtlist is None:
        continue
      meshid_to=mtlist.findtext('HeadingMappedTo/DescriptorReferredTo/DescriptorUI')
      meshterm_to=mtlist.findtext('HeadingMappedTo/DescriptorReferredTo/DescriptorName/String')
      fout.write('%s\t%s\t%s\t%s\n'%(meshid,name,meshid_to,meshterm_to))
      n_term+=1
  logging.debug('n_elem: %d'%n_elem)
  logging.info('n_term: %d'%n_term)

#############################################################################
