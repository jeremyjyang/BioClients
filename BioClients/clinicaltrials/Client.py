#!/usr/bin/env python3
"""
ClinicalTrials.gov
https://clinicaltrials.gov/api/gui/ref/api_urls
"""
### 
import sys,os,re,json,argparse,time,logging

from .. import clinicaltrials
#
#############################################################################
if __name__=='__main__':
  epilog='''\
'''
  parser = argparse.ArgumentParser(description='ClinicalTrials.gov API client', epilog=epilog)
  ops = ['listStudyFields',
	'showDataVersion',
	'showApiVersion',
	'searchStudies',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input IDs (comma-separated)")
  parser.add_argument("--query", help="Search query")
  parser.add_argument("--api_host", default=clinicaltrials.API_HOST)
  parser.add_argument("--api_base_path", default=clinicaltrials.API_BASE_PATH)
  parser.add_argument("--min_rnk", type=int, default=1, help="Minimum rank for search results.")
  parser.add_argument("--max_rnk", type=int, default=12, help="Maximum rank for search results.")
  parser.add_argument("--skip", type=int, help="")
  parser.add_argument("--nmax", type=int, help="")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
    logging.info(f"Input IDs: {len(ids)}")
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  if args.op == "showApiVersion":
    clinicaltrials.ApiVersion(api_base_url, fout)

  elif args.op == "showDataVersion":
    clinicaltrials.DataVersion(api_base_url, fout)

  elif args.op == "listStudyFields":
    clinicaltrials.ListStudyFields(api_base_url, fout)

  elif args.op == "searchStudies":
    clinicaltrials.SearchStudies(args.query, args.min_rnk, args.max_rnk, api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
