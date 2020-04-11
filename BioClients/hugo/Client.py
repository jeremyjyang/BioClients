#!/usr/bin/env python3
"""
See: http://www.genenames.org/
"""
###
import sys,os,re,argparse,time,json,logging
#
from ..util import rest_utils
from .. import hugo
#
API_HOST='rest.genenames.org'
API_BASE_PATH=''
#
##############################################################################
if __name__=='__main__':
  FTYPES=['SYMBOL','ALIAS_SYMBOL', 'HGNC_ID', 'UNIPROT', 'ENTREZ_ID', 'ENSEMBL_GENE_ID', 'VEGA_ID'];
  epilog='''\
           SYMBOL: HGNC gene symbol (e.g. ZNF3),
     ALIAS_SYMBOL: synonym gene symbol (e.g. AAA1),
          HGNC_ID: HGNC gene ID (e.g. HGNC:13089),
          UNIPROT: UniProt ID,
        ENTREZ_ID: NCBI Gene ID,
  ENSEMBL_GENE_ID: Ensembl Gene ID (e.g. ENSG00000003056),
          VEGA_ID:
'''
  parser = argparse.ArgumentParser(description='HUGO HGNC REST API client', epilog=epilog)
  ops = ['search', 'get', 'show_info', 'list_searchable']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="gene query")
  parser.add_argument("--qfile", help="query file")
  parser.add_argument("--ftypes", default="SYMBOL,ALIAS_SYMBOL", help="comma-separated list")
  parser.add_argument("--ftypes_all", type=bool, help="(could be slow)")
  parser.add_argument("--found_only", type=bool, help="no output for not-found")
  parser.add_argument("--rawquery")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  API_BASE_URL='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('ERROR: cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  qrys=[];
  if args.qfile:
    fin=open(args.qfile)
    if not fin: parser.error('ERROR: cannot open qfile: %s'%args.qfile)
    while True:
      line=fin.readline()
      if not line: break
      if line.rstrip(): qrys.append(line.rstrip())
    logging.info('input queries: %d'%(len(qrys)))
    fin.close()
  elif args.query:
    qrys.append(args.query)

  if args.ftypes_all:
    ftypes=hugo.Utils.SearchableFieldsList(API_BASE_URL)
  else:
    ftypes = re.split('[, ]+', args.ftypes.strip())
    ftypes = [s.upper() for s in ftypes]
    if len(set(ftypes) - set(FTYPES))>0:
      parser.error("Invalid field type[s]: {0}".format(set(ftypes) - set(FTYPES)))

  if args.op == "show_info":
    rval=rest_utils.GetURL(API_BASE_URL+'/info',headers={'Accept':hugo.Utils.OFMTS['JSON']},parse_json=True)
    print(json.dumps(rval,sort_keys=True,indent=2))

  elif args.op == "list_searchable":
    fields=hugo.Utils.SearchableFieldsList(API_BASE_URL)
    for i,field in enumerate(fields):
      print('\t%d. %s'%(i+1,field))

  elif args.op == "get":
    fields=hugo.Utils.SearchableFieldsList(API_BASE_URL)
    for ftype in ftypes:
      if ftype.lower() not in fields:
        parser.error("ftype \"%s\" not searchable field."%ftype)
    n_in,n_hit = hugo.Utils.GetGenes(qrys, ftypes, API_BASE_URL, fout, args.found_only, args.skip)
    logging.info('queries: %d, found: %d, not found: %d'%(n_in, n_hit, n_in-n_hit))

  elif args.op == "search":
    fields=hugo.Utils.SearchableFieldsList(API_BASE_URL)
    if ftype.lower() not in fields:
      parser.error("ftype \"%s\" not searchable field."%ftype)
    rval=hugo.Utils.SearchGenes(qrys, ftype, API_BASE_URL, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
