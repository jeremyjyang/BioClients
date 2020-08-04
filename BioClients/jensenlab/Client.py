#!/usr/bin/env python3
"""
See: https://api.jensenlab.org/About
"""
###
import sys,os,re,argparse,time,json,logging
#
from .. import jensenlab
#
API_HOST='api.jensenlab.org'
API_BASE_PATH=''
#
##############################################################################
if __name__=='__main__':
  CHANNELS= ['Knowledge', 'Experiments', 'Textmining', 'All']
  parser = argparse.ArgumentParser(description='JensenLab REST API client')
  ops = ['get_disease_genes', 'get_comention_genes' ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs (for diseases should be DOIDs, e.g. \"DOID:10652\"")
  parser.add_argument("--channel", choices=CHANNELS, default="Textmining", help="source channel")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--nmax", type=int, default=100, help="max hits")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0 = time.time()

  ids=[];
  if args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        if line.rstrip(): ids.append(line.rstrip())
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  logging.info('Input queries: %d'%(len(ids)))

  if args.op == "get_disease_genes":
    jensenlab.Utils.GetDiseaseGenes(base_url, args.channel, ids, args.nmax, fout)

  elif args.op == "get_comention_genes":
    jensenlab.Utils.GetPubmedComentionGenes(base_url, ids, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
