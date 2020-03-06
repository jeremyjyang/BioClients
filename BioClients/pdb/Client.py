#!/usr/bin/env python3
##############################################################################
### pdb_query.py - utility for PDB REST API.
### 
### See: http://www.rcsb.org/pdb/software/rest.do
##############################################################################
import sys,os,re,json,argparse,time,logging
#
from .. import pdb
#
API_HOST='www.rcsb.org'
API_BASE_PATH='/pdb/rest'
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='PDB REST API client ',
        epilog='Example keywords: ACTIN, Example UniProts: P50225')

  ops = ['list_proteins', 'list_ligands', 'search_keywords', 'search_uniprot', 'get_proteins', 'get_ligands', 'get_uniprots']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--ids", dest="ids", help="protein IDs (PDB|UniProt), comma-separated")
  parser.add_argument("--idfile", dest="idfile", help="input file, protein IDs")
  parser.add_argument("--qstr", help="search substring")
  parser.add_argument("--druglike", type=bool, help="druglike ligands only (organic, !polymer, !monoatomic)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  ids=[]
  if args.idfile:
    fin=open(args.idfile)
    if not fin: parser.error('ERROR: failed to open input file: %s'%args.idfile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids= re.split('[, ]+', args.ids.strip())

  if args.ofile:
    fout=open(args.ofile, "w+")
    if not fout: parser.error('ERROR: failed to open output file: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.op == "get_proteins":
    if not ids: parser.error('ID[s] required.')
    pdb.Utils.GetProteins(BASE_URL, ids, fout)

  elif args.op == "search_keywords":
    ids = pdb.Utils.SearchByKeywords(BASE_URL, search_keywords)
    logging.info('protein count: %d'%(len(ids)))
    pdb.Utils.GetProteins(BASE_URL, ids, fout)

  elif args.op == "search_uniprot":
    if not ids: parser.error('ID[s] required.')
    pdb.Utils.SearchByUniprot(BASE_URL, ids, fout)

  elif args.op == "list_proteins":
    pdb.Utils.ListProteins(BASE_URL, fout)

  elif args.op == "get_ligands":
    if not ids: parser.error('ID[s] required.')
    pdb.Utils.GetLigands(BASE_URL, ids, fout)

  elif args.op == "list_ligands":
    pdb.Utils.ListLigands(BASE_URL, args.druglike, fout)

  elif args.op == "get_uniprots":
    if not ids: parser.error('ID[s] required.')
    pdb.Utils.GetUniprots(BASE_URL, ids, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
