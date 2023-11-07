#!/usr/bin/env python3
"""
OWL utility functions.
https://owlready2.readthedocs.io/
"""
import sys,os,re,gzip,argparse,logging

import owlready2

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
