#!/usr/bin/env python3
#############################################################################
### https://maayanlab.cloud/sigcom-lincs/#/API 
#############################################################################
import sys,os,re,argparse,json,logging
#
from ...lincs import sigcom as sigcom_lincs
#
#############################################################################
if __name__=="__main__":
  parser = argparse.ArgumentParser(description='CLUE.IO REST API client utility')
  ops = ['getResources', ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--nmax", type=int, default=1000, help="max results")
  parser.add_argument("--skip", type=int, default=0, help="skip results")
  parser.add_argument("--api_host", default=sigcom_lincs.Utils.API_HOST)
  parser.add_argument("--api_base_path", default=sigcom_lincs.Utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.ifile:
    fin = open(args.ifile)
    ids=[];
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
    logging.info(f"input queries: {len(ids)}")
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op=='getResources':
    if not ids: parser.error('--ids or --i required.')
    sigcom_lincs.Utils.GetResources(ids, base_url, fout)

  else:
    parser.error(f"Unsupported operation: {args.op}")
