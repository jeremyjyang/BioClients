#!/usr/bin/env python3
"""
OWL utility functions.
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging

import owlready2 as or2

#############################################################################
def LoadOwlFile(ifile):
  logging.info(f"Loading {ifile}...")
  try:
    onto = or2.get_ontology(f"file://{ifile}").load()
  except Exception as e:
    logging.error(e)
    return None
  return onto

#############################################################################
def DescribeOwl(fin):
  onto = LoadOwlFile(fin.name)
  logging.info(f"base_iri: {onto.base_iri}")
  if onto.imported_ontologies:
    logging.info(f"imported_ontologies: {onto.imported_ontologies}")
  else:
    logging.info(f"imported_ontologies: (None)")
  for annot_prop in onto.metadata:
    if annot_prop is not None:
      logging.info(f"{annot_prop}:{annot_prop[onto.metadata]}")
  logging.info(f"n_classes: {len(list(onto.classes()))}")

#############################################################################
def ValidateOwl(fin):
  onto = LoadOwlFile(fin.name)
  if onto is not None:
    logging.info(f"OWL file VALIDATED: {fin.name}")
    return True
  else:
    logging.info(f"OWL file NOT VALIDATED: {fin.name}")
    return False

#############################################################################
