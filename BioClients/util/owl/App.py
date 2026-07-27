#!/usr/bin/env python3
"""
OWL utility functions.
"""
import sys,os,time,re,gzip,argparse,logging,tqdm

from .. import owl as util_owl

#############################################################################
if __name__=="__main__":
  epilog="""\
Example IRIs: (from MONDO):
http://purl.obolibrary.org/obo/MONDO_0000001,
http://purl.obolibrary.org/obo/MONDO_0005146
  """
  parser = argparse.ArgumentParser(description="OWL utility", epilog=epilog)
  ops = [ "describe_owl", "validate_owl",
         "list_classes",
         "list_all_subclasses",
         "list_subclasses",
         "list_individuals",
         "find_class",
         "get_xrefs",
         "get_synonyms",
         "show_root",
         ]
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--iris", help="node specification[s], comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file (OWL)")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile, "r") if args.ifile else sys.stdin
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.iris:
    iris = re.split(r'[,\s]+', args.iris)
  logging.info(f"Input IRIs: {len(iris)}")

  t0 = time.time()

  if args.op == "describe_owl":
    util_owl.DescribeOwl(fin)

  elif args.op == "validate_owl":
    util_owl.ValidateOwl(fin)

  elif args.op == "list_classes":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListClasses(onto, fout)

  elif args.op == "list_all_subclasses":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListAllSubclasses(onto, fout)

  elif args.op == "list_subclasses":
    if not args.iris:
      parser.error(f"--iris required for {args.op}")
    onto = util_owl.LoadOwlFile(fin)
    for iri in iris:
      c = util_owl.FindClass(onto, None, iri)
      tq = tqdm.tqdm(total=len(list(onto.classes())))
      triples = set()
      util_owl.ListSubclasses(onto, c, triples, tq, fout)
      tq.close()

  elif args.op == "list_individuals":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ListIndividuals(onto, fout)

  elif args.op == "show_root":
    onto = util_owl.LoadOwlFile(fin)
    util_owl.ShowRoot(onto)

  elif args.op == "find_class":
    if not args.iris:
      parser.error(f"--iris required for {args.op}")
    onto = util_owl.LoadOwlFile(fin)
    for iri in iris:
      c = util_owl.FindClass(onto, None, iri)

  elif args.op == "get_xrefs":
    if not args.iris:
      parser.error(f"--iris required for {args.op}")
    onto = util_owl.LoadOwlFile(fin)
    for iri in iris:
      c = util_owl.FindClass(onto, None, iri)
      util_owl.GetClassXrefs(c, fout)

  elif args.op == "get_synonyms":
    if not args.iris:
      parser.error(f"--iris required for {args.op}")
    onto = util_owl.LoadOwlFile(fin)
    for iri in iris:
      c = util_owl.FindClass(onto, None, iri)
      util_owl.GetClassSynonyms(c, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

