#!/usr/bin/env python3
"""
Utility for HuBMAP REST API.
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import hubmap as hubmap_utils
#
##############################################################################
if __name__=='__main__':
  epilog="""
Example IDs:
HBM437.HTCQ.742 (donor)
HBM525.JNPV.685 (donor)
HBM292.WDQS.245 (sample)
HBM638.DVCH.366 (sample)
HBM543.RSRV.265 (dataset)
HBM287.WDKX.539 (dataset)
HBM925.SGXL.596 (collection)
HBM876.XNRH.336 (collection)
"""
  parser = argparse.ArgumentParser(description='HuBMAP REST API client', epilog=epilog)
  ops = ['list_entity_types', 'get_entity', 
    ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, HuBMAP entity IDs or UUIDs")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--api_host", default=hubmap_utils.API_HOST)
  parser.add_argument("--api_base_path", default=hubmap_utils.API_BASE_PATH)
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

  if args.op == "list_entity_types":
    hubmap_utils.ListEntityTypes(base_url, fout)

  elif args.op == "get_entity":
    hubmap_utils.GetEntity(ids, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")
