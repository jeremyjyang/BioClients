#!/usr/bin/env python3
"""
Utility for ChEBI REST API.

* https://www.ebi.ac.uk/chebi/
* https://www.ebi.ac.uk/chebi/backend/api/docs/
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
from .. import chebi
#
##############################################################################
if __name__=='__main__':
  epilog="""\
Note that database accessions include citations.
Example entity IDs: 16737, 30273,33246,24433\
"""
  parser = argparse.ArgumentParser(description='ChEBI REST API client', epilog=epilog)
  ops = [ 
	"list_sources",
	"get_entity",
	"get_entity_names",
	"get_entity_secondary_ids",
	"get_entity_database_accessions",
	"get_entity_children",
	"get_entity_parents",
	"get_entity_origins",
	"get_compound_data",
	"search"
	]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query (Elastic search)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=chebi.API_HOST)
  parser.add_argument("--api_base_path", default=chebi.API_BASE_PATH)
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info('Input IDs: %d'%(len(ids)))

  if args.op[:3]=="get" and not (args.ifile or args.ids):
    parser.error(f"--i or --ids required for operation {args.op}.")

  if args.op == "get_entity":
    chebi.GetEntity(ids, False, False, base_url, fout)

  elif args.op == "get_entity_parents":
    chebi.GetEntity(ids, True, False, base_url, fout)

  elif args.op == "get_entity_children":
    chebi.GetEntity(ids, False, True, base_url, fout)

  elif args.op == "get_entity_database_accessions":
    chebi.GetEntityDatabaseAccessions(ids, base_url, fout)

  elif args.op == "get_entity_names":
    chebi.GetEntityNames(ids, base_url, fout)

  elif args.op == "get_compound_data":
    chebi.GetCompoundData(ids, base_url, fout)

  elif args.op == "list_sources":
    chebi.ListSources(base_url, fout)

  elif args.op == "search":
    if not args.query:
      parser.error(f'--query QUERY required for operation: {args.op}')
    #parser.error(f'Not yet implemented: {args.op}')
    chebi.Search(args.query, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')
