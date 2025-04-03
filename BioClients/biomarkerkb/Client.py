#!/usr/bin/env python3
"""
Utility for BiomarkerKB REST API.

* https://api.biomarkerkb.org/
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
from .. import biomarkerkb
#
##############################################################################
if __name__=='__main__':
  epilog="Example BiomarkerKB ID: AN6278-1"
  parser = argparse.ArgumentParser(description='BiomarkerKB REST API client', epilog=epilog)
  ops = [ 
	"get_biomarker_detail",
	"list_biomarker",
	"search_biomarker"
	]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query (SMILES)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=biomarkerkb.API_HOST)
  parser.add_argument("--api_base_path", default=biomarkerkb.API_BASE_PATH)
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

  if args.op == "get_biomarker_detail":
    biomarkerkb.GetBiomarkerDetail(ids, args.skip, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')
