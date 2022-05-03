#!/usr/bin/env python3
"""
Utility for ChEBI SOAP API.

* https://www.ebi.ac.uk/chebi/webServices.do
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
from .. import chebi
#
##############################################################################
if __name__=='__main__':
  epilog="Example entity IDs: 30273,33246,24433"
  parser = argparse.ArgumentParser(description='ChEBI SOAP API client', epilog=epilog)
  ops = [ 
	"get_entity",
	"get_entity_children",
	"get_entity_parents",
	"search"
	]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query (SMILES)")
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
    chebi.GetEntity(ids, base_url, fout)

  elif args.op == "get_entity_children":
    chebi.GetEntityChildren(ids, base_url, fout)

  elif args.op == "get_entity_parents":
    chebi.GetEntityParents(ids, base_url, fout)

  elif args.op == "search":
    parser.error(f'Not yet implemented: {args.op}')
    #chebi.Search(args.query, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')
