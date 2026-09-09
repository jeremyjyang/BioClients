#!/usr/bin/env python3
"""
See: https://docs.gdc.cancer.gov/API/Users_Guide/
"""
###
import sys,os,re,argparse,time,json,logging
#
from .. import tcga
#
API_HOST='api.gdc.cancer.gov'
API_BASE_PATH=''
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='TCGA REST API client')
  ops = [ 'list_projects', 'list_cases', 'list_files', 'list_annotations' ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  logging.info('Input queries: %d'%(len(ids)))

  if args.op == "list_projects":
    tcga.ListProjects(base_url, args.skip, args.nmax, fout)

  elif args.op == "list_cases":
    tcga.ListCases(base_url, args.skip, args.nmax, fout)

  elif args.op == "list_files":
    tcga.ListFiles(base_url, args.skip, args.nmax, fout)

  elif args.op == "list_annotations":
    tcga.ListAnnotations(base_url, args.skip, args.nmax, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
