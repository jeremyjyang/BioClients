#!/usr/bin/env python3
"""
OWL utility functions.
"""
import sys,os,re,gzip,argparse,logging

from .. import owl as util_owl

#############################################################################
if __name__=="__main__":
  epilog="""\
Example IRI (from MONDO): http://purl.obolibrary.org/obo/MONDO_0000001
  """
  parser = argparse.ArgumentParser(description="OWL utility", epilog=epilog)
  ops = [ "describe_owl", "validate_owl",
         "list_classes",
         "list_all_subclasses",
         "list_subclasses",
         "list_individuals",
         "find_iri",
         "show_root",
         ]
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--iri", help="node specification")
  parser.add_argument("--i", dest="ifile", help="input file (OWL)")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile, "r") if args.ifile else sys.stdin
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "describe_owl":
    util_owl.DescribeOwl(fin)

  elif args.op == "validate_owl":
    util_owl.ValidateOwl(fin)

  elif args.op == "list_classes":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListClasses(onto)

  elif args.op == "list_all_subclasses":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListAllSubclasses(onto)

  elif args.op == "list_subclasses":
    if not args.iri:
      parser.error(f"--iri required for {args.op}")
    onto = util_owl.LoadOwlFile(fin)
    c = util_owl.FindIri(onto, args.iri)
    util_owl.ListSubclasses(onto, c)

  elif args.op == "list_individuals":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListIndividuals(onto)

  elif args.op == "show_root":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ShowRoot(onto)

  elif args.op == "find_iri":
    onto = util_owl.LoadOwlFile(fin)
    c = util_owl.FindIri(onto, args.iri)

  else:
    parser.error(f"Invalid operation: {args.op}")
