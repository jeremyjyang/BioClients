#!/usr/bin/env python3
"""
utility app for the AMP T2D REST API.
http://www.type2diabetesgenetics.org/
http://www.kp4cd.org/apis/t2d
http://52.54.103.84/kpn-kb-openapi/

DEPICT software (Pers, TH, et al., 2015)
"""
###
import sys,os,re,json,argparse,time,logging
#
from ... import amp
#
API_HOST='public.type2diabeteskb.org'
API_BASE_PATH='/dccservices'
#
#############################################################################
if __name__=='__main__':
  ops = ["list_tissues", "list_phenotypes", "depict_genepathway"]
  parser = argparse.ArgumentParser(description="AMP T2D REST client")
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs file")
  parser.add_argument("--ids", help="input IDs, comma-separated")
  parser.add_argument("--gene", help="query gene (e.g. SLC30A8)")
  parser.add_argument("--phenotype", default="T2D")
  parser.add_argument("--max_pval", type=float, default=.0005)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.ifile:
    fin = open(args.ifile)
    ids=[]
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  t0=time.time()

  if args.op == 'list_tissues':
    amp.t2d.ListTissues(BASE_URL, fout)

  elif args.op == 'list_phenotypes':
    amp.t2d.ListPhenotypes(BASE_URL, fout)

  elif args.op == 'depict_genepathway':
    amp.t2d.DepictGenePathway(BASE_URL, args.gene, args.phenotype, args.max_pval, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

