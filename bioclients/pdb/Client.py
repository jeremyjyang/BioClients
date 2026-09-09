#!/usr/bin/env python3
"""
Utility for PDB REST API.
https://www.rcsb.org/docs/programmatic-access/web-services-overview
https://data.rcsb.org/redoc/
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import pdb as pdb_utils
#
##############################################################################
if __name__=='__main__':
  epilog="""
Example entry IDs: 3ERT, 3TTC
Example chemical IDs: CFF
"""
  parser = argparse.ArgumentParser(description='PDB REST API client', epilog=epilog)
  ops = ['list_entrys', 
    'get_entrys', 'get_chemicals', 
    ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--ids", dest="ids", help="PDB entry IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, PDB entry IDs")
  parser.add_argument("--druglike", action="store_true", help="druglike chemicals only (organic; !polymer; !monoatomic)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--api_host", default=pdb_utils.API_HOST)
  parser.add_argument("--api_base_path", default=pdb_utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = f"https://{args.api_host}{args.api_base_path}"

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  if args.op == "get_entrys":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetEntrys(ids, base_url, fout)

  elif args.op == "get_chemicals":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetChemicals(ids, args.druglike, base_url, fout)

  elif args.op == "list_entrys":
    pdb_utils.ListEntrys(base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")
