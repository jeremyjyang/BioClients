#!/usr/bin/env python3
"""
RDF utility functions.
"""
import sys,os,re,gzip,argparse,logging

import rdflib

from .. import rdf as util_rdf

#############################################################################
if __name__=="__main__":
  parser = argparse.ArgumentParser(description="RDF utility", epilog="")
  ops = ["validate", "describe", "convert", ]
  FORMATS = ["text/turtle", "application/rdf+xml", "text/n3", ]
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="input RDF file")
  parser.add_argument("--ifmt", choices=FORMATS, default="text/turtle", help="input RDF format")
  parser.add_argument("--ofmt", choices=FORMATS, default="text/turtle", help="output RDF format")
  parser.add_argument("--o", dest="ofile", help="output RDF file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile, "r") if args.ifile else sys.stdin
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "validate":
    util_rdf.Validate(fin, args.ifmt)

  elif args.op == "describe":
    util_rdf.Describe(fin, args.ifmt)

  elif args.op == "convert":
    util_rdf.Convert(fin, args.ifmt, args.ofmt, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
