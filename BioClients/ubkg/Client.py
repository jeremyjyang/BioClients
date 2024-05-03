#!/usr/bin/env python3
"""
See: https://smart-api.info/ui/55be2831c69b17f6bc975ddb58cabb5e
"""
###
import sys,os,re,argparse,time,json,logging
import pandas as pd
#
from .. import ubkg
#
##############################################################################
if __name__=='__main__':
  epilog='''\
The Data Distillery Knowledge Graph (DDKG) is an extension and instance of the Unified Biomedical Knowledge Graph (UBKG), developed by the University of Pittsburgh, Children's Hospital of Philadelphia, and the Common Fund Data Ecosystem (CFDE) Data Distillery Partnership Project.
'''
  parser = argparse.ArgumentParser(description='UBKG REST API client', epilog=epilog)
  ops = ['search',
          'info',
          'get_concept2codes',
          'get_concept2concepts',
          'get_concept2definitions',
          ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="UMLS CUI ID file")
  parser.add_argument("--ids", help="UMLS CUI IDs, comma-separated")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--api_host", default=ubkg.API_HOST)
  parser.add_argument("--api_base_path", default=ubkg.API_BASE_PATH)
  parser.add_argument("--api_key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

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
    ubkg.Info(args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2codes":
    ubkg.GetConcept2Codes(ids, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2concepts":
    ubkg.GetConcept2Concepts(ids, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2definitions":
    ubkg.GetConcept2Definitions(ids, args.api_key, BASE_URL, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
