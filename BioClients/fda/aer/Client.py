#!/usr/bin/env python3
"""
OpenFDA Adverse Event Reports REST API client.
"""
### 
import sys,os,re,json,argparse,time,yaml,logging

from ... import fda
#
API_HOST='api.fda.gov'
API_BASE_PATH='/drug/event.json'
API_KEY='==SEE $HOME/.fda.yaml=='

NMAX=100

##############################################################################
if __name__=='__main__':
  epilog='''\
Example raw query: "patient.drug.openfda.product_type:HUMAN PRESCRIPTION DRUG"
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
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_key", default=API_KEY)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  API_BASE_URL='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile,"w+")
    if not fout: parser.error('cannot open: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.op == "search":
    fda.aer.Utils.Search(args.drug_class, args.drug_ind, args.drug_unii, args.drug_ndc, args.drug_spl, args.tfrom, args.tto, args.serious, args.fatal, args.rawquery, args.NMAX, fout, API_BASE_URL, args.api_key)

  elif args.op == "info":
    rval = fda.aer.Utils.Info(API_BASE_URL)
    for field in rval.keys():
      if field=='results': continue
      print('%16s: %s'%(field,rval[field]))

  elif args.op == "counts":
    print(fda.aer.Utils.GetCounts(API_BASE_URL, args.tfrom, args.tto))

  elif args.op == "showfields":
    fields = fda.aer.Utils.GetFields(API_BASE_URL)
    for field in fields:
      print('\t%s'%field)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
