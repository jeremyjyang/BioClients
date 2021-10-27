#!/usr/bin/env python3
"""
Utility for PDB REST API.
See: http://www.rcsb.org/pdb/software/rest.do
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import pdb
#
API_HOST='www.rcsb.org'
API_BASE_PATH='/pdb/rest'
#
##############################################################################
if __name__=='__main__':
  epilog="""
Example keywords: ACTIN, Example UniProts: P50225'.
get_uniprots functionality may be discontinued by PDB.
"""
  parser = argparse.ArgumentParser(description='PDB REST API client', epilog=epilog)
  ops = ['show_counts',
    'list_proteins', 'list_ligands',
    'search',
    'get_proteins', 'get_ligands', 'get_ligands_LID2SDF',
    'get_uniprots']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="PDB IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, PDB IDs")
  parser.add_argument("--druglike", action="store_true", help="druglike ligands only (organic; !polymer; !monoatomic)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--qstr", help="search query")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.ofile:
    fout = open(args.ofile, "w+")
  else:
    fout = sys.stdout

  t0=time.time()

  if args.op == "get_proteins":
    if not ids: parser.error('ID[s] required.')
    pdb.GetProteins(BASE_URL, ids, fout)

  elif args.op == "get_uniprots":
    if not ids: parser.error('ID[s] required.')
    pdb.GetUniprots(BASE_URL, ids, fout)

  elif args.op == "get_ligands":
    if not ids: parser.error('ID[s] required.')
    pdb.GetLigands(BASE_URL, ids, args.druglike, fout)

  elif args.op == "get_ligands_LID2SDF":
    if not ids: parser.error('ID[s] required.')
    pdb.GetLigands_LID2SDF(BASE_URL, ids, fout)

  elif args.op == "list_proteins":
    pdb.ListProteins(BASE_URL, fout)

  elif args.op == "list_ligands":
    pdb.ListLigands(BASE_URL, args.druglike, fout)

  elif args.op == "show_counts":
    pdb.ShowCounts(BASE_URL)

  elif args.op == "search":
    ids = pdb.SearchByKeywords(BASE_URL, args.qstr)
    logging.info('protein count: %d'%(len(ids)))
    pdb.GetProteins(BASE_URL, ids, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
