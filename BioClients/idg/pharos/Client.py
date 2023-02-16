#!/usr/bin/env python3
"""
Pharos GraphQL API client
https://pharos.nih.gov/api
"""
###
import sys,os,argparse,json,re,time,logging
#
import gql
import python_graphql_client
#
from ...util import graphql as util_graphql
from ...idg import pharos
#
#############################################################################
def DemoGql():
  return """\
{
  search(term: "gout") {
    diseaseResult {
      count
      facets {
        facet
        values {
          name
          value
        }
      }
      diseases {
        name
        associationCount
        associations {
          did
          name
          type
        }
      }
    }
  }
}
"""

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Pharos GraphQL API client')
  ops = [
	'get_targets', 'get_diseases', 'test',
	'gql_query', 'gql_demo', ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file, target IDs")
  parser.add_argument("--i_gql", dest="ifile_gql", help="input file, GraphQL")
  parser.add_argument("--graphql", help="input GraphQL")
  parser.add_argument("--ids", dest="ids", help="IDs, target, comma-separated")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idtype_target", choices=list(pharos.IDTYPES_TARGET.keys()), default='sym', help="target ID type")
  parser.add_argument("--idtype_disease", choices=list(pharos.IDTYPES_DISEASE.keys()), default='name', help="disease ID type")
  parser.add_argument("--nmax", type=int, help="max to return")
  parser.add_argument("--api_host", default=pharos.API_HOST)
  parser.add_argument("--api_base_path", default=pharos.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = "https://"+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  logging.debug(f"gql version: {gql.__version__}")

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())
  logging.info(f"Input IDs: {len(ids)}")

  graphql=None;
  if args.ifile_gql:
    with open(args.ifile_gql) as fin:
      graphql = fin.read()
  elif args.graphql:
    graphql = args.graphql
  logging.debug(graphql)

  t0 = time.time()

  if re.match(r'^get_', args.op) and not ids:
    parser.error(f"{args.op} requires IDs.")

  if args.op=='get_targets':
    pharos.GetTargets(ids, args.idtype_target, base_url, fout)

  elif args.op=='get_diseases':
    pharos.GetDiseases(ids, args.idtype_disease, base_url, fout)

  elif args.op=='test':
    pharos.Test(base_url, fout)

  elif args.op == 'gql_query':
    util_graphql.RunQuery(graphql, base_url, fout)

  elif args.op == 'gql_demo':
    util_graphql.RunQuery(DemoGql(), base_url, fout)

  else:
    logging.error(f"Invalid operation: {args.op}")

  logging.info("Elapsed time: "+time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))
