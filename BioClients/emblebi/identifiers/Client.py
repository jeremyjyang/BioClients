#!/usr/bin/env python3
"""
EMBL-EBI Identifiers.org
https://identifiers.org
"""
### 
import sys,os,re,json,argparse,time,logging

from ... import emblebi
#
#############################################################################
if __name__=='__main__':
  epilog='''\
Example IDs: taxonomy:9606
'''
  parser = argparse.ArgumentParser(description='EMBL-EBI Identifiers.org client', epilog=epilog)
  ops = ['resolve',
	'list_namespaces',
	'list_resources',
	'list_institutions',
	'search_namespaces',
	'search_institutions',
	'search_resources',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input IDs (comma-separated)")
  parser.add_argument("--query", help="Search query.")
  parser.add_argument("--resolver_api_host", default=emblebi.identifiers.RESOLVER_API_HOST)
  parser.add_argument("--resolver_api_base_path", default=emblebi.identifiers.RESOLVER_API_BASE_PATH)
  parser.add_argument("--registry_api_host", default=emblebi.identifiers.REGISTRY_API_HOST)
  parser.add_argument("--registry_api_base_path", default=emblebi.identifiers.REGISTRY_API_BASE_PATH)
  parser.add_argument("--search_logic", choices=("containing", "exact"), default="containing")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  resolver_api_base_url = 'https://'+args.resolver_api_host+args.resolver_api_base_path
  registry_api_base_url = 'https://'+args.registry_api_host+args.registry_api_base_path

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

  if args.op == "resolve":
    emblebi.identifiers.Utils.Resolve(ids, resolver_api_base_url, fout)

  elif args.op == "list_namespaces":
    emblebi.identifiers.Utils.ListNamespaces(registry_api_base_url, fout)

  elif args.op == "list_resources":
    emblebi.identifiers.Utils.ListResources(registry_api_base_url, fout)

  elif args.op == "list_institutions":
    emblebi.identifiers.Utils.ListInstitutions(registry_api_base_url, fout)

  elif args.op == "search_namespaces":
    emblebi.identifiers.Utils.SearchNamespaces(args.query, args.search_logic, registry_api_base_url, fout)

  elif args.op == "search_institutions":
    emblebi.identifiers.Utils.SearchInstitutions(args.query, args.search_logic, registry_api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
