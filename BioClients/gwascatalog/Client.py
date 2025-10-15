#!/usr/bin/env python3
"""
GWAS Catalog REST API client.

V1:
 - https://www.ebi.ac.uk/gwas/docs/api
 - https://www.ebi.ac.uk/gwas/rest/api
 - https://www.ebi.ac.uk/gwas/rest/docs/api
 - https://www.ebi.ac.uk/gwas/rest/docs/sample-scripts

V2:
 - https://www.ebi.ac.uk/gwas/rest/api/v2/docs
 - "GWAS RESTful API V2 has been released with various enhancements & improvements over GWAS RESTful API V1. V1 is deprecated and will be retired no later than May 2026."
 - https://www.ebi.ac.uk/gwas/rest/api/v2/docs/reference

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
  parser = argparse.ArgumentParser(description='GWAS Catalog REST API (V1|V2) client', epilog=epilog)
  searchtypes=['pubmedmid', 'gcst', 'efotrait', 'efouri', 'accessionid', 'rs']
  ops = [
          'get_metadata_v2',
          'list_studies',
          'list_studies_v2',
          'get_studyAssociations',
          'get_studyAssociations_v2',
          'get_snps',
          'get_snps_v2',
          'search_studies',
          'search_studies_v2'
          ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--searchtype", choices=searchtypes, help="ID type")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=gwascatalog.API_HOST)
  parser.add_argument("--api_base_path", default=gwascatalog.API_BASE_PATH)
  parser.add_argument("--api_base_path_v2", default=gwascatalog.API_BASE_PATH_V2)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  parser.add_argument("-q", "--quiet", default=0, action="count")
  args = parser.parse_args()

  base_url = 'https://'+args.api_host+args.api_base_path
  base_url_v2 = 'https://'+args.api_host+args.api_base_path_v2

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

  if args.op == 'get_metadata_v2':
    gwascatalog.GetMetadataV2(base_url, fout)

  elif args.op == 'list_studies':
    gwascatalog.ListStudies(base_url, fout)

  elif args.op == 'list_studies_v2':
    gwascatalog.ListStudies(base_url_v2, fout)

  elif args.op == 'get_studyAssociations':
    gwascatalog.GetStudyAssociations(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_studyAssociations_v2':
    gwascatalog.GetStudyAssociationsV2(ids, args.skip, args.nmax, base_url_v2, fout)

  elif args.op == 'get_snps':
    gwascatalog.GetSnps(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_snps_v2':
    gwascatalog.GetSnpsV2(ids, args.skip, args.nmax, base_url_v2, fout)

  elif args.op == 'search_studies':
    gwascatalog.SearchStudies(ids, args.searchtype, base_url, fout)

  else:
    parser.error(f"Unknown operation: {args.op}")

  logging.info('{0}: elapsed time: {1}'.format(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

