#!/usr/bin/env python3
"""
https://query.wikidata.org/sparql

https://www.wikidata.org/wiki/User:ProteinBoxBot/SPARQL_Examples

PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX uniprotkb:<http://purl.uniprot.org/uniprot/>

GeneWiki:
  * <https://pubmed.ncbi.nlm.nih.gov/26989148/>
"""
###
import sys,os,argparse,logging
import pandas as pd

import wikidataintegrator

from .. import wikidata

#############################################################################
if __name__=="__main__":
  parser = argparse.ArgumentParser(description="Wikidata utilities", epilog="")
  ops = ["query", "list_drugTargetPairs", "list_geneDiseasePairs", ]
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--rqfile", help="input Sparql file")
  parser.add_argument("--rq", help="input Sparql string")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  logging.debug(f"Python: {sys.version.split()[0]}; wikidataintegrator: {wikidataintegrator.__version__}")

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  rq = open(args.rqfile).read() if args.rqfile else args.rq if args.rq else None

  if args.op == "query":
    if not rq: parser.error(f"--rq or --rqfile required for: {args.op}")
    wikidata.Query(rq, fout)

  elif args.op == "list_drugTargetPairs":
    wikidata.ListDrugTargetPairs(fout)

  elif args.op == "list_geneDiseasePairs":
    wikidata.ListGeneDiseasePairs(fout)

  else:
    parser.error(f"Unknown operation: {args.op}")
