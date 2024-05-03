#!/usr/bin/env python3
"""
See: https://oncotree.mskcc.org/
See: https://oncotree.mskcc.org/#/home
"""
###
import sys,os,re,argparse,time,json,logging
import pandas as pd
#
from .. import oncotree
#
##############################################################################
if __name__=='__main__':
  QUERY_TYPES = ["umls", "name", "nci", "level", "code", "mainType"]
  epilog='''\
'''
  parser = argparse.ArgumentParser(description='Oncotree REST API client', epilog=epilog)
  ops = ['search', 'get', 'info', 'list_versions', 'list_main_types', 'list_tumor_types']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="ID file")
  parser.add_argument("--ids", help="IDs, comma-separated")
  parser.add_argument("--query", help="search query")
  parser.add_argument("--query_type", choices=QUERY_TYPES, help=f"query type, one of: {QUERY_TYPES}")
  parser.add_argument("--exact_match", action="store_true", help="search criterion")
  parser.add_argument("--query_levels", default="2,3,4,5", help=f"query levels, 1-5, comma-separated list")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--api_host", default=oncotree.API_HOST)
  parser.add_argument("--api_base_path", default=oncotree.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  ids=[];
  if args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        if line.rstrip(): ids.append(line.rstrip())
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "info":
    oncotree.Info(BASE_URL, fout)

  elif args.op == "get":
    oncotree.Get(ids, args.skip, BASE_URL, fout)

  elif args.op == "list_versions":
    oncotree.ListVersions(BASE_URL, fout)

  elif args.op == "list_main_types":
    oncotree.ListMainTypes(BASE_URL, fout)

  elif args.op == "list_tumor_types":
    oncotree.ListTumorTypes(BASE_URL, fout)

  elif args.op == "search":
    oncotree.SearchTumorTypes(args.query, args.query_type, args.exact_match, args.query_levels, BASE_URL, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
