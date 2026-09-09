#!/usr/bin/env python3
"""
Pubtator REST API client
https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/RESTfulAPIs.html
Formats: JSON, PubTator, BioC.

Nomenclatures:
  Gene : NCBI Gene
e.g. https://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&term=145226
  Disease : MEDIC (CTD, CTD_diseases.csv)
e.g. http://ctdbase.org/basicQuery.go?bqCat=disease&bq=C537775
  Chemical : MESH
e.g. http://www.nlm.nih.gov/cgi/mesh/2014/MB_cgi?field=uid&term=D000596
  Species : NCBI Taxonomy
e.g. https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name=10090
  Mutation : tmVar
https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/tutorial/tmVar.html

NOTE that the API does NOT provide keyword search capability like
webapp https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/index.cgi
"""
import sys,os,time,json,argparse,re,logging
#
from .. import pubtator
#
API_HOST="www.ncbi.nlm.nih.gov"
API_BASE_PATH="/CBBresearch/Lu/Demo/RESTful/tmTool.cgi"
#
#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='PubTator REST API client', epilog='Reports PubMed NER annotations for specified PMID[s].')
  ops=['get_annotations']
  modes = ['Gene', 'Chemical', 'BioConcept']
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--mode", choices=modes, help='mode', default='BioConcept')
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--i", dest="ifile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('Input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[\s,]+', args.ids.strip())

  if args.op == 'get_annotations':
    if not ids: logging.error('Input PMIDs required.')
    pubtator.GetAnnotations(BASE_URL, args.mode, ids, fout)

  else:
    logging.error('Invalid operation: {0}'.format(args.op))
