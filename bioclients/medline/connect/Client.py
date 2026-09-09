#!/usr/bin/env python3
##############################################################################
### MedlinePlus Connect utilities - access SNOMED and ICD codes
### https://medlineplus.gov/connect/technical.html
### https://medlineplus.gov/connect/service.html
##############################################################################
### https://apps.nlm.nih.gov/medlineplus/services/mpconnect_service.cfm
### Two required parameters:
### 1. Code System (one of): 
###	ICD-10-CM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.90
###	ICD-9-CM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.103
###	SNOMED_CT: mainSearchCriteria.v.cs=2.16.840.1.113883.6.96
###	NDC: mainSearchCriteria.v.cs=2.16.840.1.113883.6.69
###	RXNORM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.88
###	LOINC:	mainSearchCriteria.v.cs=2.16.840.1.113883.6.1
### 2. Code: 
###	mainSearchCriteria.v.c=250.33
###
### Content format:
###	XML (default): knowledgeResponseType=text/xml
###	JSON: knowledgeResponseType=application/json
###	JSONP: knowledgeResponseType=application/javascript&callback=CallbackFunction
###	  where CallbackFunction is a name you give the call back function.
##############################################################################
import sys,os,re,argparse,time,logging
#
from ... import medline
#
##############################################################################
if __name__=='__main__':
  ops = ["get_code"]
  epilog = f"Supported codesystems: {sorted(medline.connect.Utils.CODESYSTEMS.keys())}"
  parser = argparse.ArgumentParser(description='MedlinePlus REST API client', epilog=epilog)
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--i", dest="ifile", help="input code ID file (one per line)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ids", help="code ID list (comma-separated)(e.g. 250.33)")
  parser.add_argument("--codesys", choices=medline.connect.Utils.CODESYSTEMS.keys(), default="RXNORM", help="code system")
  parser.add_argument("--api_host", default=medline.connect.Utils.API_HOST)
  parser.add_argument("--api_base_path", default=medline.connect.Utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info(f"Input IDs: {len(ids)}")

  if args.op=="get_code":
    medline.connect.Utils.GetCode(ids, args.codesys.upper(), api_base_url, fout)

  else:
    parser.error(f"Operation invalid: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

