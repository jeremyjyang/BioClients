#!/usr/bin/env python3
"""
	GWAS Catalog REST API client.

	https://www.ebi.ac.uk/gwas/docs/api
	https://www.ebi.ac.uk/gwas/rest/api
	https://www.ebi.ac.uk/gwas/rest/docs/api
	https://www.ebi.ac.uk/gwas/rest/docs/sample-scripts

	https://www.ebi.ac.uk/gwas/rest/api/studies/GCST004364?projection=study
	https://www.ebi.ac.uk/gwas/docs/api/studies/GCST000227/associations?projection=associationByStudy
	https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/rs6085920
"""
import sys,os,re,argparse,json,time,logging
#
from .. import gwascatalog
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/gwas/rest/api'
#
##############################################################################
if __name__=='__main__':

  epilog = "Examples: PubmedId=28530673; gcst=GCST004364; EfoUri=EFO_0004232"
  parser = argparse.ArgumentParser(description='GWAS Catalog REST API client', epilog=epilog)
  searchtypes=['pubmedmid', 'gcst', 'efotrait', 'efouri', 'accessionid', 'rs']
  ops = ['listStudies', 'searchStudies', 'getStudyAssociations', 'getSnps']
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

  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

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
    ids = re.split(r'\s*,\s*',args.ids.strip())

  if args.op == 'searchStudies':
    gwascatalog.Utils.SearchStudies(base_url, ids, args.searchtype, fout)

  elif args.op == 'listStudies':
    gwascatalog.Utils.ListStudies(base_url, fout)

  elif args.op == 'getStudyAssociations':
    gwascatalog.Utils.GetStudyAssociations(base_url, ids, fout)

  elif args.op == 'getSnps':
    gwascatalog.Utils.GetSnps(base_url, ids, fout)

  else:
    parser.error("Unknown operation: %s"%args.op)

  logging.info('{0}: elapsed time: {1}'.format(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

