#!/usr/bin/env python3
"""
Utility app for the NIH NCBI Entrez E-Utils via Entrezpy.
"""
###
import sys,os,re,argparse,time,logging
#
from .. import entrez
#
##############################################################################
if __name__=='__main__':
  OPS = [ "test", "get_esummary", "get_record", ]
  parser = argparse.ArgumentParser(description="NIH NCBI Entrez client")
  parser.add_argument("op", choices=OPS, help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="input IDs file (PMIDs)")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--email", dest="email", help="user email address")
  #parser.add_argument("--api_host", default=entrez.API_HOST)
  #parser.add_argument("--api_base_path", default=entrez.API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress notification.")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  #base_url = f"https://{args.api_host}{args.api_base_path}"

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

  if args.op == 'test':
    entrez.Test(args.email)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

