#!/usr/bin/env python3
"""
CPT Client - Current Procedural Terminology (CPT) codes. 
A tool for exploring the UMLS content from the AMA CPT.
Ref: https://www.ama-assn.org/topics/cpt-codes

https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http://www.ama-assn.org/go/cpt&version=2025&code=0031U

https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http%3A%2F%2Fwww.ama-assn.org%2Fgo%2Fcpt&version=2025&_format=json&code=0031U
"""
###
import sys,os,argparse,re,yaml,json,csv,logging,requests,time
#
from .. import umls
#
#############################################################################
if __name__=='__main__':
  EPILOG = f"""\
From the AMA website, https://www.ama-assn.org/topics/cpt-codes:
"Current Procedural Terminology (CPT) codes provide a uniform nomenclature for coding medical procedures and services. Medical CPT codes are critical to streamlining reporting and increasing accuracy and efficiency, as well as for administrative purposes such as claims processing and developing guidelines for medical care review. The AMA develops and manages CPT codes on a rigorous and transparent process led by the CPT Editorial Panel, which ensures codes are issued and updated regularly to reflect current clinical practice and innovation in medicine."
"""
  parser = argparse.ArgumentParser(description='CPT Client, an UMLS REST API client utility', epilog=EPILOG)
  ops = ['getCodes', 'search']
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="CPT code IDs (comma-separated) (ex:0153U,81441)")
  parser.add_argument("--idfile", help="input CPT code IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--searchQuery", help='string or code')
  parser.add_argument("--skip", default=0, type=int)
  parser.add_argument("--nmax", default=0, type=int)
  parser.add_argument("--api_version", default=f"{umls.API_VERSION}", help=f"API version {umls.API_VERSION}")
  parser.add_argument("--api_host", default=umls.API_HOST)
  parser.add_argument("--api_base_path", default=umls.API_BASE_PATH)
  parser.add_argument("--api_auth_host", default=umls.API_AUTH_HOST)
  parser.add_argument("--api_auth_endpoint", default=umls.API_AUTH_ENDPOINT)
  parser.add_argument("--api_auth_service", default=umls.API_AUTH_SERVICE)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.umls.yaml")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = umls.ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key
  if not params['API_KEY']:
    parser.error('Please specify valid API_KEY via --api_key or --param_file') 

  api_auth_url = 'https://'+args.api_auth_host+args.api_auth_endpoint
  auth = umls.Authentication(params['API_KEY'],
args.api_auth_service, api_auth_url, umls.API_HEADERS)
  auth.setVerbosity(args.verbose)

  ids=[];
  if args.idfile:
    fin = open(args.idfile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]', args.ids)
  if ids: logging.info(f'input IDs: {len(ids)}')

  t0 = time.time()

  if args.op == 'getCodes':
    umls.GetCodes(ids, args.srcs, auth, args.api_version, base_url, fout)

  elif args.op == 'search':
    if not args.searchQuery:
      parser.error('search requires --searchQuery')
    umls.Search(args.searchQuery, args.searchType, args.inputType, args.returnIdType, args.srcs, auth, args.api_version, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')

  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}""")
