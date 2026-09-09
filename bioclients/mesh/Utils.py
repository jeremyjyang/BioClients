#!/usr/bin/env python3
"""
MeSH XML utility functions.

MeSH XML
Download: https://www.nlm.nih.gov/mesh/download_mesh.html
Doc: https://www.nlm.nih.gov/mesh/xml_data_elements.html
"""
###
import sys,os,re,logging
#import pandas as pd
import xml.etree.cElementTree as ElementTree
from xml.parsers import expat

#############################################################################
def Desc2Csv(branch, fin, fout):
  fout.write("id\ttreenum\tterm\n")
  n_elem=0; n_term=0;
  for event, elem in ElementTree.iterparse(fin):
    meshid,meshterm,desclass,treenum = None,None,None,None;
    n_elem+=1
    logging.debug(f"""Event:{event:6s}, elem.tag:{elem.tag:6s}, elem.text:'{(elem.text.strip() if elem.text else ''):6s}'""")
    if elem.tag == "DescriptorRecord":
      if elem.attrib["DescriptorClass"] != "1": continue
      meshid,meshterm,desclass,treenum = None,None,None,None;
      meshid=elem.findtext("DescriptorUI")
      #treenum=elem.findtext("TreeNumberList/TreeNumber")
      elems = elem.findall("TreeNumberList/TreeNumber")
      treenums = map(lambda e: e.text, elems)
      for treenum in treenums:
        if (re.match(f"^{branch}", treenum)): break
      meshterm=elem.findtext("DescriptorName/String")
      #See also: ConceptList/Concept/TermList/Term/String (may be multiple)
      if not meshid:
        logging.info(f"skipping, no meshid: {elem}")
      elif not meshterm:
        logging.info(f"meshid: {meshid} ; skipping, no meshterm")
      elif not treenum:
        logging.info(f"meshid: {meshid} ; skipping, no treenum")
      elif not re.match(f"^{branch}", treenum):
        logging.info(f"meshid: {meshid} ; skipping, non-{branch} treenum: {treenum}")
      else:
        fout.write(f"{meshid}\t{treenum}\t{meshterm}\n")
        n_term+=1
  logging.info(f"n_elem: {n_elem}")
  logging.info(f"n_term: {n_term}")

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
  fout.write("id\tterm\tid_to\tterm_to\n")
  n_elem=0; n_term=0;
  for event,elem in ElementTree.iterparse(fin):
    meshid,name,meshid_to,meshterm_to = None,None,None,None;
    n_elem+=1
    logging.debug(f"""Event:{event:6s}, elem.tag:{elem.tag:6s}, elem.text:'{(elem.text.strip() if elem.text else ''):6s}'""")
    if elem.tag == "SupplementalRecord":
      scrclass = elem.attrib["SCRClass"]
      if branch not in ("C", "D"): continue
      if branch=="C" and scrclass!="3": continue #disease-only
      if branch=="D" and scrclass!="1": continue #chemical-only
      meshid=elem.findtext("SupplementalRecordUI")
      name=elem.findtext("SupplementalRecordName/String")
      mtlist=elem.find("HeadingMappedToList")
      if mtlist is None:
        continue
      meshid_to=mtlist.findtext("HeadingMappedTo/DescriptorReferredTo/DescriptorUI")
      meshterm_to=mtlist.findtext("HeadingMappedTo/DescriptorReferredTo/DescriptorName/String")
      fout.write(f"{meshid}\t{name}\t{meshid_to}\t{meshterm_to}\n")
      n_term+=1
  logging.info(f"n_elem: {n_elem}")
  logging.info(f"n_term: {n_term}")

#############################################################################
