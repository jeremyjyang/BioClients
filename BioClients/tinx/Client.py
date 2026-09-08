#!/usr/bin/env python3
"""
Access to TINX REST API.
TINX = Target Importance & Novelty Explorer
"""
import sys,os,re,argparse,time,logging
#
from .. import tinx
#
##############################################################################
if __name__=='__main__':
  epilog = '''Example IDs:\
          Diseases: DOID:0014667
          Targets: 488
'''
  parser = argparse.ArgumentParser(description='TINX REST API query client', epilog=epilog)
  ops = [
    'get_disease_targets',
    'get_disease_publications',
    'get_target_diseases',
    'get_target_publications',
    'search_diseases',
    'search_targets',
         ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="UniProt IDs, comma-separated (ex: Q14790)")
  parser.add_argument("--i", dest="ifile", help="input file, UniProt IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", dest="search_query", help="search query")
  parser.add_argument("--api_host", default=tinx.API_HOST)
  parser.add_argument("--api_base_path", default=tinx.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

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

  if args.op == 'get_disease_targets':
    if not ids: parser.error('--i or --ids required.')
    tinx.GetDiseaseTargets(ids, base_url, fout)

  elif args.op == 'get_target_diseases':
    if not ids: parser.error('--i or --ids required.')
    tinx.GetTargetDiseases(ids, base_url, fout)

  elif args.op == 'search_diseases':
    tinx.SearchDiseases(search_query, base_url, fout)

  else:
    parser.error(f"Unknown operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

