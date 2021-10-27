#!/usr/bin/env python3
"""
GeneOntology client.
"""
###
import os,sys,argparse,re,json,time,logging
import urllib.parse

from .. import geneontology
#
##############################################################################
if __name__=='__main__':
  epilog="""\
"""
  parser = argparse.ArgumentParser(description='GeneOntolgy API client', epilog=epilog)
  ops=['list_terms', 'list_genes', 'get_entities', 'get_geneTerms' ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--ids", help="ID list (comma-separated)(e.g. NCBIGene:84570, GO:0006954)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--api_host", default=geneontology.API_HOST)
  parser.add_argument("--api_base_path", default=geneontology.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.ids:
    ids = re.split(r'[,\s]+', args.ids.strip())
  elif args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        ids.append(line.rstrip())

  if args.op == 'list_terms':
    geneontology.ListTerms(BASE_URL, fout)

  elif args.op == 'list_genes':
    geneontology.ListGenes(BASE_URL, fout)

  elif args.op == 'get_entities':
    geneontology.GetEntities(ids, BASE_URL, fout)

  elif args.op == 'get_geneTerms':
    geneontology.GetGeneTerms(ids, BASE_URL, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')

