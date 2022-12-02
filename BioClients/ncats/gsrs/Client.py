#!/usr/bin/env python3
"""
https://ncats.nih.gov/expertise/preclinical/gsrs
https://gsrs.ncats.nih.gov/
https://gsrs.ncats.nih.gov/#/api
"""
### 
import sys,os,re,json,argparse,time,logging

from ... import ncats
#
#############################################################################
if __name__=='__main__':
  epilog='''\
Example search queries:
IBUPRO
ASPIRIN
OXYTOCIN
OXYTO*
ASPIRIN AND ESTER
COCN
C=1CC=CC=C1C(=O)O
'''
  parser = argparse.ArgumentParser(description='NCATS Global Substance Registration System (GSRS) client', epilog=epilog)
  ops = [
	'list_vocabularies',
	'list_substances',
	'search',
	'get_substance',
	'get_substance_names',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input IDs (comma-separated)")
  parser.add_argument("--query", help="Search query.")
  parser.add_argument("--api_host", default=ncats.gsrs.API_HOST)
  parser.add_argument("--api_base_path", default=ncats.gsrs.API_BASE_PATH)
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

  if args.op == "list_vocabularies":
    ncats.gsrs.Utils.ListVocabularies(api_base_url, fout)

  elif args.op == "list_substances":
    ncats.gsrs.Utils.ListSubstances(api_base_url, fout)

  elif args.op == "search":
    ncats.gsrs.Utils.Search(args.query, api_base_url, fout)

  elif args.op == "get_substance":
    ncats.gsrs.Utils.GetSubstance(ids, api_base_url, fout)

  elif args.op == "get_substance_names":
    ncats.gsrs.Utils.GetSubstanceNames(ids, api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
