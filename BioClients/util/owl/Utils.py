#!/usr/bin/env python3
"""
OWL utility functions.
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging,tqdm
import pandas as pd
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
  props = list(onto.properties())
  props.sort()
  for prop in props:
    logging.info(f"property:{prop}")
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
def FindClass(onto, label, iri):
  if label:
    c = onto.search_one(label = label)
  else:
    c = onto.search_one(iri = iri)
  if c is not None:
    logging.debug(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}")
  else:
    logging.error(f"NOT FOUND: label={label}, iri={iri}")
  return c

#############################################################################
def ListSubclasses(onto, c, triples, tq, fout):
  n_subclass=0;
  for sc in onto.search(subclass_of = c):
    if sc == c: continue
    key = f"{c.name}\t{sc.name}"
    if key in triples: continue
    else: triples.add(key)
    n_subclass+=1
    tq.update(1)
    logging.debug(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\t{sc.namespace.name}\t{sc.namespace.base_iri}\t{sc.name}\t{';'.join(sc.label)}\t{sc.iri}")
    fout.write(f"{c.namespace.name}\t{c.namespace.base_iri}\t{c.name}\t{';'.join(c.label)}\t{c.iri}\t{sc.namespace.name}\t{sc.namespace.base_iri}\t{sc.name}\t{';'.join(sc.label)}\t{sc.iri}\n")
    n_subclass += ListSubclasses(onto, sc, triples, tq, fout)
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
def GetClassXrefs(iris, onto, fout):
  df=None; n_xref_out=0; n_err=0;
  tq = tqdm.tqdm(total=len(iris))
  for iri in iris:
    c = FindClass(onto, None, iri)
    if not c:
      n_err+=1
      continue

    sabs_this=[]; vals_this=[];
    for xref in c.hasDbXref:
      sab,val = re.split(':', xref)
      logging.debug(f"{xref}\tsab:{sab}\tvalue:{val}")
      sabs_this.append(sab)
      vals_this.append(val)

    df_this = pd.DataFrame({
      'class_name':[c.name for i in range(len(vals_this))],
      'class_iri':[c.iri for i in range(len(vals_this))],
      'xref_sab':sabs_this,
      'xref_value':vals_this})
    df_this.to_csv(fout, sep='\t', index=False, header=bool(n_xref_out==0))
    n_xref_out+=df_this.shape[0]
    tq.update(1)
  tq.close()
  logging.info(f"n_iri: {len(iris)}; n_xref_out: {n_xref_out}; n_err: {n_err}")

#############################################################################
def GetClassSynonyms(iris, onto, fout):
  df=None; n_syn_out=0; n_err=0;
  tq = tqdm.tqdm(total=len(iris))
  for iri in iris:
    c = FindClass(onto, None, iri)
    if not c:
      n_err+=1
      continue

    vals_this = list(c.hasExactSynonym)
    vals_this.sort()
    df_this = pd.DataFrame({
      'class_name':[c.name for i in range(len(vals_this))],
      'class_iri':[c.iri for i in range(len(vals_this))],
      'exact_synonym':vals_this})
    df_this.to_csv(fout, sep='\t', index=False, header=bool(n_syn_out==0))
    n_syn_out+=df_this.shape[0]
    tq.update(1)
  tq.close()
  logging.info(f"n_iri: {len(iris)}; n_syn_out: {n_syn_out}; n_err: {n_err}")

#############################################################################
# Should this get a function?
# props = c.get_class_properties()
#

#############################################################################
def ListIndividuals(onto, fout):
  n_ind=0;
  for ind in onto.individuals():
    fout.write(f"{ind.namespace.name}\t{ind.namespace.base_iri}\t{ind.name}\t{';'.join(ind.label)}\t{ind.iri}\n")
    n_ind+=1
  logging.info(f"n_ind: {n_ind}")

#############################################################################
