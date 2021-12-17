#!/usr/bin/env python3
###
import sys,os,json,argparse,logging

from ...util import graphql as util_graphql

#GQL_HOST="ncats-ifx.appspot.com"
GQL_HOST="pharos-api.ncats.io"
GQL_BASE_PATH="/graphql"
GQL_URL="https://"+GQL_HOST+GQL_BASE_PATH

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
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Pharos GraphQL client utility')
  OPS = ['query', 'demo', 'getSchema']
  parser.add_argument("op", choices=OPS, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file, GraphQL")
  parser.add_argument("--graphql", help="input GraphQL")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--gql_host", default=GQL_HOST)
  parser.add_argument("--gql_base_path", default=GQL_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  gql_url='https://'+args.gql_host+args.gql_base_path

  fout = open(args.ofile) if args.ofile else sys.stdout

  graphql=None;
  if args.ifile:
    with open(args.ifile) as fin:
      graphql = fin.read()
  elif args.graphql:
    graphql = args.graphql
  logging.debug(graphql)

  if args.op == 'query':
    util_graphql.RunQuery(gql_url, graphql, fout)

  elif args.op == 'demo':
    util_graphql.RunQuery(gql_url, DemoGql(), fout)

  elif args.op == 'getSchema':
    parser.error(f"Unimplemented operation: {args.op}")

  else:
    parser.error(f"Invalid operation: {args.op}")

