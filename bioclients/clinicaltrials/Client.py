#!/usr/bin/env python3
"""
ClinicalTrials.gov
https://clinicaltrials.gov/api/gui/ref/api_urls
API v2.0: https://clinicaltrials.gov/data-api/api
https://clinicaltrials.gov/data-api/about-api/csv-download
"""
### 
import sys,os,re,json,argparse,time,logging

from .. import clinicaltrials
#
#############################################################################
if __name__=='__main__':
  epilog='''\
See:
https://clinicaltrials.gov/data-api/about-api, 
https://clinicaltrials.gov/data-api/api, 
https://clinicaltrials.gov/find-studies/constructing-complex-search-queries
'''
  parser = argparse.ArgumentParser(description='ClinicalTrials.gov API client', epilog=epilog)
  ops = [ 'version',
	'list_study_fields', 'list_search_areas', 'list_enums',
	'search_studies', 'get_studies', ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input NCT_IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input NCT_IDs (comma-separated)")
  parser.add_argument("--query_cond", help="Search query condition")
  parser.add_argument("--query_term", help="Search query term")
  parser.add_argument("--api_host", default=clinicaltrials.API_HOST)
  parser.add_argument("--api_base_path", default=clinicaltrials.API_BASE_PATH)
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

  if args.op == "version":
    clinicaltrials.Version(api_base_url, fout)

  elif args.op == "list_study_fields":
    clinicaltrials.ListStudyFields(api_base_url, fout)

  elif args.op == "list_search_areas":
    clinicaltrials.ListSearchAreas(api_base_url, fout)

  elif args.op == "list_enums":
    clinicaltrials.ListEnums(api_base_url, fout)

  elif args.op == "search_studies":
    clinicaltrials.SearchStudies(args.query_cond, args.query_term, api_base_url, fout)

  elif args.op == "get_studies":
    clinicaltrials.GetStudies(ids, api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
