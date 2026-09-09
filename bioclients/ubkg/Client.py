#!/usr/bin/env python3
"""
See: https://smart-api.info/ui/55be2831c69b17f6bc975ddb58cabb5e
"""
###
import sys,os,re,argparse,time,json,logging
import pandas as pd
#
from .. import ubkg
from .. import umls
#
##############################################################################
if __name__=='__main__':
  epilog='''\
The Data Distillery Knowledge Graph (DDKG) is a context (extension) of the Unified Biomedical Knowledge Graph (UBKG), developed by the University of Pittsburgh, Children's Hospital of Philadelphia, and the Common Fund Data Ecosystem (CFDE) Data Distillery Partnership Project.
'''
  parser = argparse.ArgumentParser(description='UBKG REST API client', epilog=epilog)
  ops = ['search',
          'info',
          'list_relationship_types',
          'list_node_types',
          'list_node_type_counts',
          'list_property_types',
          'list_sabs',
          'list_sources',
          'list_semantic_types',
          'get_concept2codes',
          'get_concept2concepts',
          'get_concept2definitions',
          'get_concept2paths',
          'get_concept2trees',
          'get_term2concepts',
          ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="UMLS CUI ID file")
  parser.add_argument("--ids", help="UMLS CUI IDs, comma-separated")
  parser.add_argument("--term", help="UMLS term, e.g. 'Asthma'")
  parser.add_argument("--sab", help="Standard abbreviation type")
  parser.add_argument("--relationship", default="isa", help="Relationship type")
  parser.add_argument("--context", choices=ubkg.CONTEXTS, default="base_context")
  parser.add_argument("--mindepth", type=int, default=1, help="min path depth")
  parser.add_argument("--maxdepth", type=int, default=3, help="max path depth")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--api_host", default=ubkg.API_HOST)
  parser.add_argument("--api_base_path", default=ubkg.API_BASE_PATH)
  parser.add_argument("--api_key", help="UMLS API Key")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.umls.yaml")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  params = umls.ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key
  if not params['API_KEY']:
    parser.error('Please specify valid UMLS API_KEY via --api_key or --param_file')

  t0=time.time()

  ids=[];
  if args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        if line.rstrip(): ids.append(line.rstrip())
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "info":
    ubkg.Info(args.api_key, BASE_URL, fout)

  elif args.op == "list_relationship_types":
    ubkg.ListRelationshipTypes(args.api_key, BASE_URL, fout)

  elif args.op == "list_node_types":
    ubkg.ListNodeTypes(args.api_key, BASE_URL, fout)

  elif args.op == "list_node_type_counts":
    ubkg.ListNodeTypeCounts(args.api_key, BASE_URL, fout)

  elif args.op == "list_property_types":
    ubkg.ListPropertyTypes(args.api_key, BASE_URL, fout)

  elif args.op == "list_semantic_types":
    ubkg.ListSemanticTypes(args.api_key, BASE_URL, fout)

  elif args.op == "list_sabs":
    ubkg.ListSABs(args.api_key, BASE_URL, fout)

  elif args.op == "list_sources":
    ubkg.ListSources(args.context, args.sab, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2codes":
    ubkg.GetConcept2Codes(ids, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2concepts":
    ubkg.GetConcept2Concepts(ids, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2definitions":
    ubkg.GetConcept2Definitions(ids, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2paths":
    if not args.sab: parser.error(f"--sab required for operation: {args.op}")
    ubkg.GetConcept2Paths(ids, args.sab, args.relationship, args.mindepth, args.maxdepth, args.api_key, BASE_URL, fout)

  elif args.op == "get_concept2trees":
    if not args.sab: parser.error(f"--sab required for operation: {args.op}")
    ubkg.GetConcept2Trees(ids, args.sab, args.relationship, args.mindepth, args.maxdepth, args.api_key, BASE_URL, fout)

  elif args.op == "get_term2concepts":
    ubkg.GetTerm2Concepts(args.term, args.api_key, BASE_URL, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
