#!/usr/bin/env python3
"""
OWL utility functions.
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging

import owlready2 as or2

#############################################################################
def LoadOwlFile(fin):
  logging.info(f"Loading {fin.name}...")
  try:
    onto = or2.get_ontology(f"file://{fin.name}").load()
  except Exception as e:
    logging.error(e)
    return None
  return onto

#############################################################################
def DescribeOwl(fin):
  onto = LoadOwlFile(fin)
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
  onto = LoadOwlFile(fin)
  if onto is not None:
    logging.info(f"OWL file VALIDATED: {fin.name}")
    return True
  else:
    logging.info(f"OWL file NOT VALIDATED: {fin.name}")
    return False

#############################################################################
def ListClasses(onto):
  n_class=0;
  for c in onto.classes():
    logging.debug(f"{str(c)}\t{c.iri}")
    n_class+=1
  logging.info(f"n_class: {n_class}")

#############################################################################
def ListSubclasses(onto):
  n_class=0; n_subclass=0;
  for c in onto.classes():
    n_class+=1
    logging.debug(f"{str(c)}\t{c.iri}")
    for sc in onto.search(subclass_of = c):
      n_subclass+=1
      logging.debug(f"{c.namespace}\t{c.name}\t{c.label}\t{c.iri}\t{sc.namespace}\t{sc.name}\t{sc.label}\t{sc.iri}")
  logging.info(f"n_class: {n_class}; n_subclass: {n_subclass}")

#############################################################################
def ListIndividuals(onto):
  n_ind=0;
  for ind in onto.individuals():
    logging.debug(f"{ind.name}\t{ind.iri}")
    n_ind+=1
  logging.info(f"n_ind: {n_ind}")

#############################################################################
