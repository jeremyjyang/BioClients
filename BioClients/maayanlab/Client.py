#!/usr/bin/env python3
"""
See: http://amp.pharm.mssm.edu/Harmonizome/documentation
"""
###
import sys,os,re,argparse,time,json,logging
#
from .. import maayanlab
#
#
##############################################################################
if __name__=='__main__':
  API_HOST='amp.pharm.mssm.edu'
  API_BASE_PATH='/Harmonizome/api/1.0'
  parser = argparse.ArgumentParser(description='MaayanLab Harmonizome REST API client')
  ops = [ 'get_gene', 'get_gene_associations' ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
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

  if args.op == "get_gene":
    maayanlab.Utils.GetGene(base_url, ids, fout)

  elif args.op == "get_gene_associations":
    maayanlab.Utils.GetGeneAssociations(base_url, ids, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
