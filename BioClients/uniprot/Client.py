#!/usr/bin/env python3
"""
Access to Uniprot REST API.
https://www.uniprot.org/help/api
UniprotKB = Uniprot Knowledge Base

python3 -m BioClients.uniprot.Client --uids Q14790 getData
"""
import sys,os,re,argparse,time,logging
#
from .. import uniprot
#
API_HOST='www.uniprot.org'
API_BASE_PATH='/uniprot'
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Uniprot query client; get data for specified IDs')
  ops = ['getData', 'listData']
  ofmts = ['txt', 'tab', 'xml', 'rdf', 'fasta', 'gff']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--uids", dest="uids", help="UniProt IDs, comma-separated (ex: Q14790)")
  parser.add_argument("--i", dest="ifile", help="input file, UniProt IDs")
  parser.add_argument("--o", dest="ofile", help="output (CSV)")
  parser.add_argument("--ofmt", default='txt')
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URI='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

  t0=time.time()

  uids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      uids.append(line.strip())
  elif args.uids:
    uids = re.split(r'[\s,]+', args.uids.strip())
  else:
    parser.error('--i or --uids required.')

  if args.op == 'getData':
    uniprot.GetData(BASE_URI, uids, args.ofmt, fout)

  else:
    parser.error('Unknown operation: %s'%args.op)

  logging.info('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

