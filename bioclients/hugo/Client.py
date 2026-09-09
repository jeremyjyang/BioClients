#!/usr/bin/env python3
"""
See: http://www.genenames.org/
"""
###
import sys,os,re,argparse,time,json,logging
import pandas as pd
#
from ..util import rest
from .. import hugo
#
##############################################################################
if __name__=='__main__':
  FTYPES=['SYMBOL', 'ALIAS_SYMBOL', 'PREV_SYMBOL', 'HGNC_ID', 'UNIPROT', 'ENTREZ_ID', 'ENSEMBL_GENE_ID', 'VEGA_ID'];
  epilog='''\
           SYMBOL: HGNC gene symbol (e.g. ZNF3),
     ALIAS_SYMBOL: synonym gene symbol (e.g. AAA1),
          HGNC_ID: HGNC gene ID (e.g. HGNC:13089),
          UNIPROT: UniProt ID,
        ENTREZ_ID: NCBI Gene ID,
  ENSEMBL_GENE_ID: Ensembl Gene ID (e.g. ENSG00000003056),
'''
  parser = argparse.ArgumentParser(description='HUGO HGNC REST API client', epilog=epilog)
  ops = ['search', 'get', 'info', 'list_searchable']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="query file")
  parser.add_argument("--query", help="gene query")
  parser.add_argument("--ftypes", default="SYMBOL,ALIAS_SYMBOL,PREV_SYMBOL", help="comma-separated list")
  parser.add_argument("--ftypes_all", action="store_true", help="(could be slow)")
  parser.add_argument("--rawquery", action="store_true")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--api_host", default=hugo.API_HOST)
  parser.add_argument("--api_base_path", default=hugo.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    qrys=[];
    with open(args.ifile) as fin:
      while True:
        line=fin.readline()
        if not line: break
        if line.rstrip(): qrys.append(line.rstrip())
  elif args.query:
    qrys = [args.query]

  if args.ftypes_all:
    ftypes = list(hugo.ListSearchableFields(BASE_URL).iloc[:,0])
  else:
    ftypes = re.split('[, ]+', args.ftypes.strip())
    ftypes = [s.upper() for s in ftypes]
    if len(set(ftypes) - set(FTYPES))>0:
      parser.error("Invalid field type[s]: {0}".format(set(ftypes) - set(FTYPES)))

  if args.op == "info":
    hugo.Info(BASE_URL, fout)

  elif args.op == "list_searchable":
    hugo.ListSearchableFields(BASE_URL, fout)

  elif args.op == "get":
    hugo.GetGenes(qrys, ftypes, args.skip, BASE_URL, fout)

  elif args.op == "search":
    hugo.SearchGenes(qrys, ftypes, BASE_URL, fout)

  else:
    parser.error("Invalid operation: {}".format(args.op))

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
