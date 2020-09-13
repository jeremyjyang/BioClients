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
  verstr = ('Python: {}; wikidataintegrator: {}'.format(sys.version.split()[0], wikidataintegrator.__version__))
  parser = argparse.ArgumentParser(description='Wikidata utilities with biomedical focus', epilog=verstr)
  ops = ['list_drugTargetPairs', 'list_geneDiseasePairs', 'test']
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--rqfile", help="input Sparql file")
  parser.add_argument("--rq", help="input Sparql string")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  logging.debug(verstr)

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == 'test':
    wikidata.Utils.Test(fout)

  elif args.op == 'list_DrugTargetPairs':
    wikidata.Utils.ListDrugTargetPairs(fout)

  elif args.op == 'list_GeneDiseasePairs':
    wikidata.Utils.ListGeneDiseasePairs(fout)

  else:
    parser.error('Unknown operation: {}'.format(args.op))
