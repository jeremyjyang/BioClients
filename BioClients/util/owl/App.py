#!/usr/bin/env python3
"""
OWL utility functions.
"""
import sys,os,re,gzip,argparse,logging

from .. import owl as util_owl

#############################################################################
if __name__=="__main__":
  parser = argparse.ArgumentParser(description="OWL utility", epilog="")
  ops = [ "describe_owl", "validate_owl", ]
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="input file (OWL)")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile, "r") if args.ifile else sys.stdin
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "describe_owl":
    util_owl.DescribeOwl(args.ifile)

  elif args.op == "validate_owl":
    util_owl.ValidateOwl(args.ifile)

  else:
    parser.error(f"Invalid operation: {args.op}")
