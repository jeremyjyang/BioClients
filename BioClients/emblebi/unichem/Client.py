#!/usr/bin/env python3
"""
EMBL-EBI Unichem
https://chembl.gitbook.io/unichem/webservices
"""
### 
import sys,os,re,json,argparse,time,logging

from ... import emblebi
#
#############################################################################
if __name__=='__main__':
  epilog='''\

'''
  parser = argparse.ArgumentParser(description='EMBL-EBI Unichem client', epilog=epilog)
  ops = ['getFromSourceId', 'listSources', 'getFromInchi', 'getFromInchikey'
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="Input IDs")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--ids", help="Input IDs (comma-separated)")
  parser.add_argument("--src_id_in", help="")
  parser.add_argument("--src_id_out", help="")
  parser.add_argument("--api_host", default=emblebi.unichem.API_HOST)
  parser.add_argument("--api_base_path", default=emblebi.unichem.API_BASE_PATH)
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

  if args.op == "getFromSourceId":
    emblebi.unichem.Utils.GetFromSourceId(ids, args.src_id_in, args.src_id_out, api_base_url, fout)

  elif args.op == "getFromInchi":
    parser.error(f"Unimplemented: {args.op}")

  elif args.op == "getFromInchikey":
    parser.error(f"Unimplemented: {args.op}")

  elif args.op == "listSources":
    emblebi.unichem.Utils.ListSources(api_base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
