#!/usr/bin/env python3
"""
RDF utility functions.
https://rdflib.readthedocs.io/
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging

import rdflib
import owlready2

#############################################################################
def LoadRdfFile(fin, ifmt):
  g = rdflib.Graph()
  try:
    g.parse(fin, format=ifmt)
    logging.info(f"RDF graph from {fin.name} ({ifmt}) contains {len(g)} triples.")
  except Exception as e:
    logging.error(e)
    return None
  return g

#############################################################################
def ValidateRdf(fin, ifmt):
  g = LoadRdfFile(fin, ifmt)
  if g is not None:
    logging.info(f"RDF file VALIDATED: {fin.name} ({ifmt})")
    return True
  else:
    logging.info(f"RDF file NOT VALIDATED: {fin.name} ({ifmt})")
    return False

#############################################################################
def DescribeRdf(fin, ifmt):
  g = LoadRdfFile(fin, ifmt)

#############################################################################
def ConvertRdf(fin, ifmt, ofmt, fout):
  g = LoadRdfFile(fin, ifmt)
  fout.write(g.serialize(format=ofmt).decode("utf8"))
  logging.info(f"RDF graph to {fout.name} ({ofmt}) containing {len(g)} triples.")

#############################################################################
def LoadOwlFile(ifile):
  try:
    onto = owlready2.get_ontology(f"file://{ifile}").load()
    logging.info(f"OWL ontology from {ifile} contains {len(list(onto.classes()))} classes.")
  except Exception as e:
    logging.error(e)
    return None
  return onto

#############################################################################
def DescribeOwl(ifile):
  onto = LoadOwlFile(ifile)

#############################################################################
def ValidateOwl(ifile):
  onto = LoadOwlFile(ifile)
  if onto is not None:
    logging.info(f"OWL file VALIDATED: {ifile}")
    return True
  else:
    logging.info(f"OWL file NOT VALIDATED: {ifile}")
    return False

#############################################################################
