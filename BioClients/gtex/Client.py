#!/usr/bin/env python3
"""
Utility for GTEx REST API.

* https://www.gtexportal.org/home/api-docs/
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
from .. import gtex
#
##############################################################################
if __name__=='__main__':
  epilog=""
  parser = argparse.ArgumentParser(description='GTEx REST API client', epilog=epilog)
  ops = [ 
	"list_datasets",
	"list_subjects",
	"list_samples",
	"get_gene_expression"
	]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dataset", default="gtex_v8", help="GTEx datasetId")
  parser.add_argument("--subject", help="GTEx subjectId")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=gtex.API_HOST)
  parser.add_argument("--api_base_path", default=gtex.API_BASE_PATH)
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info('Input IDs: %d'%(len(ids)))

  if args.op[:3]=="get" and not (args.ifile or args.ids):
    parser.error(f"--i or --ids required for operation {args.op}.")

  if args.op == "list_datasets":
    gtex.ListDatasets(base_url, fout)

  elif args.op == "list_subjects":
    gtex.ListSubjects(args.dataset, base_url, fout)

  elif args.op == "list_samples":
    gtex.ListSamples(args.dataset, args.subject, base_url, fout)

  elif args.op == "get_gene_expression":
    gtex.GetGeneExpression(ids, args.dataset, args.skip, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')
