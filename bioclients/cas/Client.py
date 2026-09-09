#!/usr/bin/env python3
"""
Utility app for the CAS REST API.
"""
###
import sys,os,re,argparse,time,logging
#
from .. import cas
#
##############################################################################
if __name__=='__main__':
  ops = ["get_rn2details", "get_rn2image"]
  parser = argparse.ArgumentParser(description="CAS REST client")
  parser.add_argument("op", choices=ops,help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input IDs file (CAS Registry Number)")
  parser.add_argument("--ids", help="input IDs (CAS Registry Number) (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--api_host", default=cas.API_HOST)
  parser.add_argument("--api_base_path", default=cas.API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  logging.info(f"Input IDs: {len(ids)}")

  t0=time.time()

  if args.op == 'get_rn2details':
    cas.GetRN2Details(ids, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

