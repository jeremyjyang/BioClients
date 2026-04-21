#!/usr/bin/env python3
"""
Access to Uniprot REST API.
UniprotKB = Uniprot Knowledge Base
"""
import sys,os,re,argparse,time,logging
#
from .. import uniprot
#
##############################################################################
if __name__=='__main__':
  epilog = 'Example IDs: Q14790,P01116,P01118,A8K8Z5,B0LPF9,Q96D10'
  parser = argparse.ArgumentParser(description='Uniprot query client; get data for specified IDs', epilog=epilog)
  ops = ['getData',
         'getNames',
         'getFunctions',
         'listData']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="UniProt IDs, comma-separated (ex: Q14790)")
  parser.add_argument("--i", dest="ifile", help="input file, UniProt IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=uniprot.API_HOST)
  parser.add_argument("--api_base_path", default=uniprot.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URI='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  t0=time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'[\s,]+', args.ids.strip())
  else:
    parser.error('--i or --ids required.')

  if args.op == 'getData':
    uniprot.GetData(BASE_URI, ids, fout)

  elif args.op == 'getNames':
    uniprot.GetNames(BASE_URI, ids, fout)

  elif args.op == 'getFunctions':
    uniprot.GetFunctions(BASE_URI, ids, fout)

  else:
    parser.error(f"Unknown operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

