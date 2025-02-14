#!/usr/bin/env python3
"""
    https://www.disgenet.com/Profile-area#howtouse
"""
###
import sys,os,re,argparse,time,logging
#
from .. import disgenet
from ..util import yaml as util_yaml
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='Disgenet.org REST API client utility',
        epilog="""\
Example IDs: C0019829 (UMLS CUI); 351 (NCBI Gene ID) """)
  ops = ['search_diseases', 'get_diseases', 'get_disease_GDAs', 'get_gene_GDAs', 'get_version']
  parser.add_argument("op",choices=ops,help='OPERATION')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated (Disease UMLS CUIs, or Gene EntrezIDs, HGNC symbols, or UniProtIDs)")
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--source", choices=disgenet.SOURCES, default="CURATED", help="default=CURATED")
  parser.add_argument("--disease_type", choices=disgenet.DISEASE_TYPES, default="disease")
  parser.add_argument("--disease_classes", help="List of MeSH disease classes, comma-separated, e.g. C01 for Infections")
  parser.add_argument("--geneid_type", choices=disgenet.GENEID_TYPES, default="ncbi")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--nmax", type=int, default=None, help="max results")
  parser.add_argument("--api_host", default=disgenet.API_HOST)
  parser.add_argument("--api_base_path", default=disgenet.API_BASE_PATH)
  #parser.add_argument("--user_email")
  #parser.add_argument("--user_password")
  parser.add_argument("--api_key")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.disgenet.yaml")
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if os.path.isfile(args.param_file):
    params = util_yaml.ReadParamFile(args.param_file)
  #if args.user_email: params['EMAIL'] = args.user_email 
  #if args.user_password: params['PASSWORD'] = args.user_password
  if args.api_key: params['API_KEY'] = args.api_key

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    fin = open(args.ifile)
    ids = [];
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    logging.info(f"Input queries: {len(ids)}")
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "get_disease_GDAs":
    disgenet.GetDiseaseGDAs(ids, args.source, params["API_KEY"], base_url, fout)

  elif args.op == "get_gene_GDAs":
    disgenet.GetGeneGDAs(ids, args.geneid_type, args.source, params["API_KEY"], base_url, fout)

  elif args.op == "get_diseases":
    disgenet.GetDiseases(ids, args.disease_type, args.disease_classes, args.nmax, params["API_KEY"], base_url, fout)

  elif args.op == "search_diseases":
    disgenet.SearchDiseases(args.query, args.source, args.disease_type, args.disease_class, args.nmax, params["API_KEY"], base_url, fout)

  elif args.op == "get_version":
    disgenet.GetVersion(params["API_KEY"], base_url, fout)

  else:
    parser.error("No operation specified.")

  logging.info(f"elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
