#!/usr/bin/env python3
"""
https://orders.atcddd.fhi.no/atc
https://api.atcddd.fhi.no/swagger/
"""
### 
import sys,os,re,json,argparse,time,yaml,logging

from ... import who
from ...util import yaml as util_yaml
#
#############################################################################
if __name__=='__main__':
  epilog='''\
'''
  parser = argparse.ArgumentParser(description='WHO ATC client', epilog=epilog)
  ops = [
	'list_alterations_for_year',
	'list_new_for_year',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--year", type=int, default=time.gmtime(time.time()).tm_year, help="year of alterations")
  parser.add_argument("--api_host", default=who.atc.API_HOST)
  parser.add_argument("--api_base_path", default=who.atc.API_BASE_PATH)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.who_atc.yaml")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = util_yaml.ReadParamFile(args.param_file)
  if args.api_key: params['API_JWT_TOKEN'] = args.api_key
  if not params['API_JWT_TOKEN']:
    parser.error('Please specify valid API_KEY via --api_key or --param_file') 

  t0=time.time()

  if args.op == "list_alterations_for_year":
    who.atc.Utils.ListAlterations(args.year, params['API_JWT_TOKEN'], api_base_url, fout)

  elif args.op == "list_new_for_year":
    who.atc.Utils.ListNew(args.year, params['API_JWT_TOKEN'], api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
