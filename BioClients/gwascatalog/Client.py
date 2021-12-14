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
##############################################################################
if __name__=='__main__':
  epilog = """\
Example PMIDs: 28530673;
Example GCSTs: GCST004364, GCST000227;
Example EFOIDs: EFO_0004232;
Example SNPIDs: rs6085920, rs2273833, rs6684514, rs144991356
"""
  parser = argparse.ArgumentParser(description='GWAS Catalog REST API client', epilog=epilog)
  searchtypes=['pubmedmid', 'gcst', 'efotrait', 'efouri', 'accessionid', 'rs']
  ops = ['list_studies', 'search_studies', 'get_studyAssociations', 'get_snps']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--searchtype", choices=searchtypes, help="ID type")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=gwascatalog.API_HOST)
  parser.add_argument("--api_base_path", default=gwascatalog.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  parser.add_argument("-q", "--quiet", default=0, action="count")
  args = parser.parse_args()

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  t0 = time.time()

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())
  if ids: logging.info(f"Input IDs: {len(ids)}")

  if args.op == 'search_studies':
    gwascatalog.SearchStudies(ids, args.searchtype, base_url, fout)

  elif args.op == 'list_studies':
    gwascatalog.ListStudies(base_url, fout)

  elif args.op == 'get_studyAssociations':
    gwascatalog.GetStudyAssociations(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_snps':
    gwascatalog.GetSnps(ids, args.skip, args.nmax, base_url, fout)

  else:
    parser.error(f"Unknown operation: {args.op}")

  logging.info('{0}: elapsed time: {1}'.format(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

