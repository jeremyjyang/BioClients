#!/usr/bin/env python3
"""
Utility functions for the NLM ChemIDplus REST API.
https://chem.nlm.nih.gov/chemidsearch/api
https://chem.nlm.nih.gov/api/swagger-ui.html
https://chem.nlm.nih.gov/api/v2/api-docs
"""
###
import sys,os,re,argparse,time,logging
#
from .. import chemidplus
#
##############################################################################
if __name__=='__main__':
  ops = ["list_sources", "list_types", "get_id2summary", "get_id2names",
	"get_id2numbers",
	"get_id2toxlist"]
  parser = argparse.ArgumentParser(description="ChemIDPlus REST client")
  parser.add_argument("op", choices=ops,help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input IDs file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--id_type", default="auto", help="input ID type")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--api_host", default=chemidplus.API_HOST)
  parser.add_argument("--api_base_path", default=chemidplus.API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  logging.info(f"Input IDs: {len(ids)}")

  t0=time.time()

  if args.op == 'list_sources':
    chemidplus.ListSources(base_url, fout)

  elif args.op == 'list_types':
    chemidplus.ListTypes(base_url, fout)

  elif args.op == 'get_id2summary':
    chemidplus.GetId2Summary(ids, args.id_type, base_url, fout)

  elif args.op == 'get_id2names':
    chemidplus.GetId2Names(ids, args.id_type, base_url, fout)

  elif args.op == 'get_id2numbers':
    chemidplus.GetId2Numbers(ids, args.id_type, base_url, fout)

  elif args.op == 'get_id2toxlist':
    chemidplus.GetId2ToxicityList(ids, args.id_type, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

