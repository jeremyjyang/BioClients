#!/usr/bin/env python3
"""
 https://www.disgenet.org/api/
 https://www.disgenet.org/dbinfo
 DisGeNET Disease Types : disease, phenotype, group
 DisGeNET Metrics:
   GDA Score
   VDA Score
   Disease Specificity Index (DSI)
   Disease Pleiotropy Index (DPI)
   Evidence Level (EL)
   Evidence Index (EI)
 GNOMAD pLI (Loss-of-function Intolerant)

 DisGeNET Association Types:
   Therapeutic
   Biomarker
   Genomic Alterations
   GeneticVariation
   Causal Mutation
   Germline Causal Mutation
   Somatic Causal Mutation
   Chromosomal Rearrangement
   Fusion Gene
   Susceptibility Mutation
   Modifying Mutation
   Germline Modifying Mutation
   Somatic Modifying Mutation
   AlteredExpression
   Post-translational Modification
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
        description='Disgenet (www.disgenet.org) REST API client utility',
        epilog="""\
Example IDs: C0019829 (UMLS CUI); 351 (NCBI Gene ID) """)
  ops = ['list_diseases', 'get_diseases', 'get_disease_GDAs', 'get_gene_GDAs', 'get_protein_GDAs']
  parser.add_argument("op",choices=ops,help='OPERATION')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated (Disease UMLS CUIs, or Gene EntrezIDs, HGNC symbols, or UniProtIDs)")
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--source", choices=disgenet.SOURCES, default="ALL", help="default=ALL")
  parser.add_argument("--disease_type", choices=disgenet.DISEASE_TYPES, default="disease")
  parser.add_argument("--disease_class", choices=disgenet.DISEASE_CLASSES, help="MeSH disease class")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--nmax", type=int, default=None, help="max results")
  parser.add_argument("--api_host", default=disgenet.API_HOST)
  parser.add_argument("--api_base_path", default=disgenet.API_BASE_PATH)
  parser.add_argument("--user_email")
  parser.add_argument("--user_password")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.disgenet.yaml")
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if os.path.isfile(args.param_file):
    params = util_yaml.ReadParamFile(args.param_file)
  if args.user_email: params['EMAIL'] = args.user_email 
  if args.user_password: params['PASSWORD'] = args.user_password
  logging.debug(f"EMAIL: \"{params['EMAIL']}\"; PASSWORD: \"{params['PASSWORD']}\"")

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
    disgenet.GetDiseaseGDAs(ids, args.source, params["EMAIL"], params["PASSWORD"], base_url, fout)

  elif args.op == "get_gene_GDAs":
    disgenet.GetGeneGDAs(ids, args.source, params["EMAIL"], params["PASSWORD"], base_url, fout)

  elif args.op == "get_protein_GDAs":
    disgenet.GetProteinGDAs(ids, args.source, params["EMAIL"], params["PASSWORD"], base_url, fout)

  elif args.op == "get_diseases":
    disgenet.GetDiseases(args.source, args.disease_type, args.disease_class, args.nmax, params["EMAIL"], params["PASSWORD"], base_url, fout)

  elif args.op == "list_diseases":
    disgenet.ListDiseases(params["EMAIL"], params["PASSWORD"], base_url, fout)

  else:
    parser.error("No operation specified.")

  logging.info(f"elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
