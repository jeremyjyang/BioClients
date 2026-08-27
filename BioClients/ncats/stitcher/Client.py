#!/usr/bin/env python3
"""
https://drugs.ncats.io/
https://stitcher.ncats.io/api/
https://stitcher.ncats.io/api/stitches/latest/8R78F6L9VO
https://github.com/ncats/stitcher
https://academic.oup.com/nar/article/50/D1/D1307/6396888
"""
### 
import sys,os,re,json,argparse,time,logging

from ... import ncats
#
#############################################################################
if __name__=='__main__':
  epilog='''\
Example UNIIs:
8R78F6L9VO
EM8BM710ZC
WI4X0X7BPJ
884KT10YB7
2679MF687A
'''
  parser = argparse.ArgumentParser(description='NCATS Inxight Drugs API client', epilog=epilog)
  ops = [
	'get_drug',
	'get_drug_targets',
	'search',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input UNII IDs (comma-separated)")
  parser.add_argument("--query", help="Search query.")
  parser.add_argument("--api_host", default=ncats.stitcher.API_HOST)
  parser.add_argument("--api_base_path", default=ncats.stitcher.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = 'https://'+args.api_host+args.api_base_path

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
    logging.info(f"Input IDs: {len(ids)}")
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  if args.op == "get_drug":
    ncats.stitcher.Utils.GetDrug(ids, api_base_url, fout)

  elif args.op == "get_drug_targets":
    ncats.stitcher.Utils.GetDrugTargets(ids, api_base_url, fout)

  elif args.op == "search":
    ncats.stitcher.Utils.Search(args.query, api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
