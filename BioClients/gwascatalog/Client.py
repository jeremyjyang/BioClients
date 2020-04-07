#!/usr/bin/env python3
"""
GWAS Catalog REST API client.

https://www.ebi.ac.uk/gwas/docs/api
https://www.ebi.ac.uk/gwas/rest/api
https://www.ebi.ac.uk/gwas/rest/docs/api
https://www.ebi.ac.uk/gwas/rest/docs/sample-scripts
"""
import sys,os,re,argparse,json,time,logging
#
from .. import gwascatalog
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/gwas/rest/api'
#
##############################################################################
if __name__=='__main__':
  epilog = "Examples: PubmedId=28530673; gcst=GCST004364,GCST000227; EfoUri=EFO_0004232; snpId=rs6085920"
  parser = argparse.ArgumentParser(description='GWAS Catalog REST API client', epilog=epilog)
  searchtypes=['pubmedmid', 'gcst', 'efotrait', 'efouri', 'accessionid', 'rs']
  ops = ['list_studies', 'search_studies', 'get_studyAssociations', 'get_snps']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--searchtype", choices=searchtypes, help="ID type")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  t0 = time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())

  if args.op == 'search_studies':
    gwascatalog.Utils.SearchStudies(base_url, ids, args.searchtype, fout)

  elif args.op == 'list_studies':
    gwascatalog.Utils.ListStudies(base_url, fout)

  elif args.op == 'get_studyAssociations':
    gwascatalog.Utils.GetStudyAssociations(base_url, ids, fout)

  elif args.op == 'get_snps':
    gwascatalog.Utils.GetSnps(base_url, ids, fout)

  else:
    parser.error("Unknown operation: {0}".format(args.op))

  logging.info('{0}: elapsed time: {1}'.format(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

