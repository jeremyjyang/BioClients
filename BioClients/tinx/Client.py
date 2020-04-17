#!/usr/bin/env python3
"""
TIN-X (Target Importance and Novelty Explorer) REST API client
https://www.newdrugtargets.org/
https://api.newdrugtargets.org/docs
https://api.newdrugtargets.org/targets/
"""
###
import sys,os,re,argparse,time,logging
#
from .. import tinx
#
API_HOST="api.newdrugtargets.org"
API_BASE_PATH=""
#
##############################################################################
if __name__=='__main__':
  epilog="""\
"""
  parser = argparse.ArgumentParser(description="TIN-X (Target Importance and Novelty Explorer) REST API client)", epilog=epilog)
  ops = [
	"list_diseases",
	"list_targets",
	"list_articles",
	"list_dtos",
	"get_disease",
	"get_disease_targets",
	"get_disease_target_articles",
	"get_target",
	"get_target_diseases",
	"get_dto",
	"search"]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input IDs")
  parser.add_argument("--ids", help="IDs (comma-separated)")
  parser.add_argument("--disease_ids", help="disease IDs (comma-separated), needed ONLY if BOTH target and disease IDs specified")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

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
    ids = re.split('[, ]+', args.ids.strip())
  if ids: logging.info('Input IDs: %d'%(len(ids)))
  if args.disease_ids:
    disease_ids = re.split('[, ]+', args.disease_ids.strip())

  t0=time.time()

  base_url = 'https://'+args.api_host+args.api_base_path

  if args.op=='list_targets':
    tinx.Utils.ListTargets(base_url, args.skip, args.nmax, fout)

  elif args.op=='list_diseases':
    tinx.Utils.ListDiseases(base_url, args.skip, args.nmax, fout)

  else:
    parser.error('Unknown operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
