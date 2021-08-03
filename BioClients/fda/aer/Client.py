#!/usr/bin/env python3
"""
OpenFDA Adverse Event Reports REST API client.
https://open.fda.gov/apis/
"""
### 
import sys,os,re,json,argparse,time,yaml,logging

from ... import fda
#
#############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

##############################################################################
if __name__=='__main__':
  NMAX=100;
  epilog='''\
Example UNII: 786Z46389E
'''
  parser = argparse.ArgumentParser(description='OpenFDA Adverse Event Reports client', epilog=epilog)
  ops = ['search', 'counts', 'info', 'showfields']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--drug_class", help="EPC pharmacologic class")
  parser.add_argument("--drug_ind", help="drug indication")
  parser.add_argument("--drug_unii", help="drug ID UNII")
  parser.add_argument("--drug_ndc", help="drug ID NDC")
  parser.add_argument("--drug_spl", help="drug ID SPL")
  parser.add_argument("--serious", type=bool, help="serious adverse events")
  parser.add_argument("--fatal", type=bool, help="fatal adverse events (seriousnessdeath)")
  parser.add_argument("--tfrom", help="time-from (received by FDA) (YYYYMMDD)")
  parser.add_argument("--tto", default=time.strftime('%Y%m%d',time.localtime()), help="time-to (received by FDA) (YYYYMMDD)")
  parser.add_argument("--rawquery")
  parser.add_argument("--nmax", type=int, default=NMAX, help="max returned records")
  parser.add_argument("--api_host", default=fda.aer.API_HOST)
  parser.add_argument("--api_base_path", default=fda.aer.API_BASE_PATH)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.fda.yaml")
  parser.add_argument("--api_key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key
  if not params['API_KEY']:
    parser.error('Please specify valid API_KEY via --api_key or --param_file')

  t0=time.time()

  if args.op == "search":
    fda.aer.Utils.Search(args.drug_class, args.drug_ind, args.drug_unii, args.drug_ndc, args.drug_spl, args.tfrom, args.tto, args.serious, args.fatal, args.rawquery, args.nmax, params['API_KEY'], api_base_url, fout)

  elif args.op == "info":
    rval = fda.aer.Utils.Info(api_base_url)
    for field in rval.keys():
      if field=='results': continue
      print(f"{field:16s}: {rval[field]}")

  elif args.op == "counts":
    print(fda.aer.Utils.GetCounts(args.tfrom, args.tto, api_base_url))

  elif args.op == "showfields":
    fields = fda.aer.Utils.GetFields(api_base_url)
    for field in fields:
      print(f"\t{field}")

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
