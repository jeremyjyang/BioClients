#!/usr/bin/env python3
#############################################################################
### CDC  REST API client
### https://tools.cdc.gov/api/docs/info.aspx
### https://tools.cdc.gov/api/v2/resources
#############################################################################
import sys,os,argparse,re,time,logging
#
from .. import cdc
#
#############################################################################
if __name__=='__main__':
  API_HOST="tools.cdc.gov"
  API_BASE_PATH="/api/v2/resources"
  ops = ["list_sources", "list_topics", "list_organizations", "list_audiences"]
  parser = argparse.ArgumentParser( description='CDC REST API client utility')
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--i", dest="ifile", help="input file")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.op=="list_sources":
    cdc.ListResources(api_base_url, 'sources', fout)

  elif args.op=="list_topics":
    cdc.ListResources(api_base_url, 'topics', fout)

  elif args.op=="list_organizations":
    cdc.ListResources(api_base_url, 'organizations', fout)

  elif args.op=="list_audiences":
    cdc.ListResources(api_base_url, 'audiences', fout)

  else:
    parser.error('Operation invalid: {}'.format(args.op))
