#!/usr/bin/env python3
"""
RDF utility functions.
"""
import sys,os,re,gzip,argparse,logging

import rdflib

#############################################################################
def LoadGraph(fin, ifmt):
  g = rdflib.Graph()
  try:
    g.parse(fin, format=ifmt)
    logging.info(f"RDF graph from {fin.name} ({ifmt}) contains {len(g)} triples.")
  except Exception as e:
    logging.error(e)
    return None
  return g

#############################################################################
def Validate(fin, ifmt):
  g = LoadGraph(fin, ifmt)
  if g is not None:
    logging.info(f"RDF file VALIDATED: {fin.name} ({ifmt})")
    return True
  else:
    logging.info(f"RDF file NOT VALIDATED: {fin.name} ({ifmt})")
    return False

#############################################################################
def Describe(fin, ifmt):
  g = LoadGraph(fin, ifmt)

#############################################################################
def Convert(fin, ifmt, ofmt, fout):
  g = LoadGraph(fin, ifmt)
  fout.write(g.serialize(format=ofmt).decode("utf8"))
  logging.info(f"RDF graph to {fout.name} ({ofmt}) containing {len(g)} triples.")

#############################################################################
