#!/usr/bin/env python3
"""
CPT Client - Current Procedural Terminology (CPT) codes. 
A tool for exploring the UMLS content from the AMA CPT.
Ref: https://www.ama-assn.org/topics/cpt-codes

https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http://www.ama-assn.org/go/cpt&version=2025&code=0031U

https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http%3A%2F%2Fwww.ama-assn.org%2Fgo%2Fcpt&version=2025&code=0031U

https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http://www.ama-assn.org/go/cpt&version=2025&code=0113U
"""
###
import sys,os,argparse,re,yaml,json,logging,requests,urllib,time
#
from .. import umls
#
API_HOST="cts.nlm.nih.gov"
API_BASE_PATH="/fhir/res/CodeSystem"
API_CODE_SYSTEM="http://www.ama-assn.org/go/cpt"
API_CODE_VERSION="2025"
#
#############################################################################
def CPTLogin(api_key):
  url_this = "https://cts.nlm.nih.gov/fhir/login"
  headers = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate, br, zstd',
          'Content-Type': 'application/x-www-form-urlencoded',
          #'Origin': 'https://cts.nlm.nih.gov',
          'Connection': 'keep-alive',
          'Referer': 'https://cts.nlm.nih.gov/fhir/login.html'
          }
  data = {
          'username':'apikey',
          'password':api_key
          }
  response = requests.post(url_this, headers=headers, data=data)
  if (response.status_code!=200):
    logging.error(f"(status_code={response.status_code};{response.reason};{response.text}): url_this: {url_this}")
    return
  else:
    logging.debug(f"(status_code={response.status_code};{response.reason};{response.text}): url_this: {url_this}")

  rval = response.json()
  if rval:
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))

  return

#############################################################################
def GetCPTCodes(ids, api_key, base_url, fout=None):
  """
  https://cts.nlm.nih.gov/fhir/res/CodeSystem/$lookup?system=http://www.ama-assn.org/go/cpt&version=2025&code=0113U

  How to include api key in header?
"""


  headers = {
          "Accept": "application/json"
          }
  n_out=0; df=None;
  for id_this in ids:
    url_this = f"{base_url}&code={id_this}"
    response = requests.get(url_this, headers=headers)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code};{response.reason};{response.text}): url_this: {url_this}")
      continue
    rval = response.json()
    if not rval: continue
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))


    df_this = pd.DataFrame({'CPT_code':[id_this], 'name': 'TBA'})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out+=1
  logging.info(f'n_id: {len(ids)}')
  logging.info(f'n_out: {n_out}')
  if fout is None: return df

#############################################################################
if __name__=='__main__':
  EPILOG = f"""\
From the AMA website, https://www.ama-assn.org/topics/cpt-codes:
"Current Procedural Terminology (CPT) codes provide a uniform nomenclature for coding medical procedures and services. Medical CPT codes are critical to streamlining reporting and increasing accuracy and efficiency, as well as for administrative purposes such as claims processing and developing guidelines for medical care review. The AMA develops and manages CPT codes on a rigorous and transparent process led by the CPT Editorial Panel, which ensures codes are issued and updated regularly to reflect current clinical practice and innovation in medicine."
"""
  parser = argparse.ArgumentParser(description='CPT Client, an UMLS REST API client utility', epilog=EPILOG)
  ops = ['getCodes', 'login']
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="CPT code IDs (comma-separated) (ex:0153U,81441)")
  parser.add_argument("--idfile", help="input CPT code IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--searchQuery", help='string or code')
  parser.add_argument("--skip", default=0, type=int)
  parser.add_argument("--nmax", default=0, type=int)
  #parser.add_argument("--api_version", default=f"{API_VERSION}", help=f"API version {API_VERSION}")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_code_system", default=API_CODE_SYSTEM)
  parser.add_argument("--api_code_version", default=API_CODE_VERSION)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.umls.yaml")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = f"https://{args.api_host}{args.api_base_path}/$lookup?system={urllib.parse.quote(args.api_code_system)}&version={args.api_code_version}"

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = umls.ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key
  if not params['API_KEY']:
    parser.error('Please specify valid API_KEY via --api_key or --param_file') 

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
    GetCPTCodes(ids, params['API_KEY'], base_url, fout)

  elif args.op == 'login':
    CPTLogin(params['API_KEY'])

  else:
    parser.error(f'Invalid operation: {args.op}')

  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}""")
