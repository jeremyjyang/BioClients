#! /usr/bin/env python3
"""
Developed and tested with doid.obo (Disease Ontology).
"""
import sys,os,argparse,re,logging

from .. import obo as util_obo

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='OBO to TSV converter')
  parser.add_argument("--i", dest="ifile", required=True, help="input OBO file")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile)

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  util_obo.OBO2CSV(fin, fout)
