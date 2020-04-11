#!/usr/bin/env python3
"""
GeneOntology client.
"""
###
import os,sys,argparse,re,json,time,logging
import urllib.parse

from .. import geneontology

API_HOST='api.geneontology.org'
API_BASE_PATH='/api'
#
##############################################################################
if __name__=='__main__':
  epilog="""\
"""
  parser = argparse.ArgumentParser(description='GeneOntolgy API client', epilog=epilog)
  ops=['list_Terms', 'list_Genes', 'get_Entities', 'get_GeneTerms' ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--ids", help="ID list (comma-separated)(e.g. NCBIGene:84570, GO:0006954)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w+")
  else:
    fout = sys.stdout

  if args.ids:
    ids = re.split(r'[,\s]+', args.ids.strip())
  elif args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        ids.append(line.rstrip())

  if args.op == 'list_Terms':
    geneontology.Utils.ListTerms(BASE_URL, fout)

  elif args.op == 'list_Genes':
    geneontology.Utils.ListGenes(BASE_URL, fout)

  elif args.op == 'get_Entities':
    geneontology.Utils.GetEntities(BASE_URL, ids, fout)

  elif args.op == 'get_GeneTerms':
    geneontology.Utils.GetGeneTerms(BASE_URL, ids, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

