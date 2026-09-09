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
    'get_target_diseases',
    'get_disease_target_publications',
    'search_diseases',
    'search_targets',
         ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids_disease", help="IDs, comma-separated (DOIDs for diseases)")
  parser.add_argument("--ids_target", help="IDs, comma-separated (TINX_IDs for targets)")
  parser.add_argument("--ifile_disease", help="input file, DOIDs")
  parser.add_argument("--ifile_target", help="input file, TINX_IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--n_max_hit", type=int, default=tinx.N_MAX_HIT, help="max hits per query ID")
  parser.add_argument("--query", dest="search_query", help="search query")
  parser.add_argument("--api_host", default=tinx.API_HOST)
  parser.add_argument("--api_base_path", default=tinx.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  t0=time.time()

  ids_disease=[];
  if args.ifile_disease:
    fin = open(args.ifile_disease)
    while True:
      line = fin.readline()
      if not line: break
      ids_disease.append(line.strip())
  elif args.ids_disease:
    ids_disease = re.split(r'[\s,]+', args.ids_disease.strip())

  ids_target=[];
  if args.ifile_target:
    fin = open(args.ifile_target)
    while True:
      line = fin.readline()
      if not line: break
      ids_target.append(line.strip())
  elif args.ids_target:
    ids_target = re.split(r'[\s,]+', args.ids_target.strip())

  if args.op == "get_disease_targets":
    if not ids_disease: parser.error(f"--ifile_disease or --ids_disease required for: {args.op}")
    tinx.GetDiseaseTargets(ids_disease, args.n_max_hit, base_url, fout)

  elif args.op == "get_target_diseases":
    if not ids_target: parser.error(f"--ifile_target or --ids_target required for: {args.op}")
    tinx.GetTargetDiseases(ids_target, args.n_max_hit, base_url, fout)

  elif args.op == "get_disease_target_publications":
    if not ids_disease: parser.error(f"--ifile_disease or --ids_disease required for: {args.op}")
    if not ids_target: parser.error(f"--ifile_target or --ids_target required for: {args.op}")
    tinx.GetDiseaseTargetPublications(ids_disease, ids_target, args.n_max_hit, base_url, fout)

  elif args.op == "search_diseases":
    tinx.SearchDiseases(search_query, args.n_max_hit, base_url, fout)

  else:
    parser.error(f"Unknown operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

