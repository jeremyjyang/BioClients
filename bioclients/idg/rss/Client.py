#!/usr/bin/env python3
"""
IDG Resource Submission System
https://rss.ccs.miami.edu/
"""
###
import sys,os,re,argparse,time,logging
#
from ...idg import rss
#
##############################################################################
if __name__=='__main__':
  epilog="""\
"""
  parser = argparse.ArgumentParser(description="IDG RSS (Resource Submission System) REST API client)", epilog=epilog)
  ops = [ "list_targets", "get_target_resources" ]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input IDs")
  parser.add_argument("--ids", help="IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=rss.Utils.API_HOST)
  parser.add_argument("--api_base_path", default=rss.Utils.API_BASE_PATH)
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
    ids = re.split('[,\s]+', args.ids.strip())
  if ids: logging.info('Input IDs: %d'%(len(ids)))

  t0=time.time()

  base_url = 'https://'+args.api_host+args.api_base_path

  if args.op=='list_targets':
    rss.Utils.ListTargets(base_url, fout)

  elif args.op=='get_target_resources':
    if not ids: parser.error(f"--i or --ids required for {args.op}")
    rss.Utils.GetTargetResources(ids, base_url, fout)

  else:
    parser.error(f'Unknown operation: {args.op}')

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
