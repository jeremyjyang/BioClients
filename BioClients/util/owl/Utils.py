#!/usr/bin/env python3
"""
OWL utility functions.
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging,tqdm

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
def ListClasses(onto, fout):
  n_class=0;
  tq = tqdm.tqdm(total=len(list(onto.classes())))
  for c in onto.classes():
    tq.update(1)
    fout.write(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\n")
    n_class+=1
  tq.close()
  logging.info(f"n_class: {n_class}")

#############################################################################
def FindIri(onto, iri):
  c = onto.search_one(iri = iri)
  if c is not None:
    logging.info(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}")
  else:
    logging.error(f"NOT FOUND: {iri}")
  return c

#############################################################################
def ListSubclasses(onto, c, tq, fout):
  n_subclass=0;
  for sc in onto.search(subclass_of = c):
    if sc == c: continue
    n_subclass+=1
    tq.update(1)
    logging.debug(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\t{sc.namespace.name}\t{sc.namespace.base_iri}\t{sc.name}\t{';'.join(sc.label)}\t{sc.iri}")
    fout.write(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\t{sc.namespace.name}\t{sc.namespace.base_iri}\t{sc.name}\t{';'.join(sc.label)}\t{sc.iri}\n")
    n_subclass += ListSubclasses(onto, sc, tq, fout)
  if n_subclass>0:
    logging.debug(f"Subclasses-of: {c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}, n_subclass: {n_subclass}")
  return n_subclass

#############################################################################
def ListAllSubclasses(onto, fout):
  n_class=0; n_subclass=0;
  tq = tqdm.tqdm(total=len(list(onto.classes())))
  for c in onto.classes():
    tq.update(1)
    n_class+=1
    for sc in onto.search(subclass_of = c):
      if sc == c: continue
      n_subclass+=1
      fout.write(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\t{sc.namespace.name}\t{sc.namespace.base_iri}\t{sc.name}\t{';'.join(sc.label)}\t{sc.iri}\n")
  tq.close()
  logging.info(f"n_class: {n_class}; n_subclass: {n_subclass}")

#############################################################################
def ListIndividuals(onto, fout):
  n_ind=0;
  for ind in onto.individuals():
    fout.write(f"{ind.namespace.name}\t{ind.namespace.base_iri}\t{ind.name}\t{';'.join(ind.label)}\t{ind.iri}\n")
    n_ind+=1
  logging.info(f"n_ind: {n_ind}")

#############################################################################
