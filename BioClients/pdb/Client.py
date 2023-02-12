#!/usr/bin/env python3
"""
Utility for PDB REST API.
https://www.rcsb.org/docs/programmatic-access/web-services-overview
https://data.rcsb.org/redoc/
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import pdb as pdb_utils
#
##############################################################################
if __name__=='__main__':
  epilog="""
Example keywords: ACTIN, Example UniProts: P50225'.
get_uniprots functionality may be discontinued by PDB.
"""
  parser = argparse.ArgumentParser(description='PDB REST API client', epilog=epilog)
  ops = ['show_counts', 'list_proteins', 'list_ligands', 'search',
    'get_proteins', 'get_ligands', 'get_ligands_LID2SDF',
    'get_uniprots']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="PDB IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, PDB IDs")
  parser.add_argument("--druglike", action="store_true", help="druglike ligands only (organic; !polymer; !monoatomic)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--qstr", help="search query")
  parser.add_argument("--api_host", default=pdb_utils.API_HOST)
  parser.add_argument("--api_base_path", default=pdb_utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = f"https://{args.api_host}{args.api_base_path}"

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  if args.op == "get_proteins":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetProteins(ids, base_url, fout)

  elif args.op == "get_uniprots":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetUniprots(ids, base_url, fout)

  elif args.op == "get_ligands":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetLigands(ids, args.druglike, base_url, fout)

  elif args.op == "get_ligands_LID2SDF":
    if not ids: parser.error('ID[s] required.')
    pdb_utils.GetLigands_LID2SDF(ids, base_url, fout)

  elif args.op == "list_proteins":
    pdb_utils.ListProteins(base_url, fout)

  elif args.op == "list_ligands":
    pdb_utils.ListLigands(args.druglike, base_url, fout)

  elif args.op == "show_counts":
    pdb_utils.ShowCounts(base_url)

  elif args.op == "search":
    ids = pdb_utils.SearchByKeywords(args.qstr, base_url)
    logging.info(f"protein count: {len(ids)}")
    pdb_utils.GetProteins(ids, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")
