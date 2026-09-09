#!/usr/bin/env python3
"""
PubMed iCite  REST API client
https://icite.od.nih.gov/api
"""
###
import sys,os,re,argparse,logging
#
from .. import icite

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='PubMed iCite REST API client utility', epilog='Publication metadata.')
  ops = ['get_stats']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--i", dest="ifile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--year", help="list: year of publication")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=icite.API_HOST)
  parser.add_argument("--api_base_path", default=icite.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress notification.")
  args = parser.parse_args()

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  base_url='https://'+args.api_host+args.api_base_path

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
    if not ids: parser.error(f'Operation requires PMID[s]: {args.op}')
    icite.GetStats(ids, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

