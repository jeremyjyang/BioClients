#!/usr/bin/env python3
"""
PubMed iCite  REST API client
https://icite.od.nih.gov/api
"""
###
import sys,os,argparse,logging
import urllib.request,json,re
#
from .. import icite

#############################################################################
if __name__=='__main__':
  API_HOST="icite.od.nih.gov"
  API_BASE_PATH="/api/pubs"
  #
  parser = argparse.ArgumentParser(description='PubMed iCite REST API client utility', epilog='Publication metadata.')
  ops = ['get_stats']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--i", dest="ifile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--year", help="list: year of publication")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w", encoding="utf-8") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('Input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[\s,]+', args.ids.strip())

  if args.op == 'get_stats':
    if not ids: parser.error('Requires PMID[s].')
    icite.Utils.GetStats(BASE_URL, ids, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

