#!/usr/bin/env python3
"""
Access to Ensembl REST API.
http://rest.ensembl.org/documentation/info/lookup
"""
import sys,os,re,argparse,time,json,logging

from .. import ensembl
#
API_HOST='rest.ensembl.org'
API_BASE_PATH=''
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(prog=sys.argv[0], description="Ensembl REST API client", epilog="Example ID: ENSG00000157764")
  ops = ["list_species", "get_xrefs", "get_info", "show_version"]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="Ensembl_IDs, comma-separated (ex:ENSG00000000003)")
  parser.add_argument("--i", dest="ifile", help="input file, Ensembl_IDs")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    fin = open(args.ifile)
    ids=[]
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())

  if re.match("^get_", args.op) and not ids:
    parser.error('--i or --ids required.')

  if args.op=='list_species':
    ensembl.Utils.ListSpecies(BASE_URL, fout)

  elif args.op=='get_info':
    ensembl.Utils.GetInfo(BASE_URL, ids, fout)

  elif args.op=='get_xrefs':
    ensembl.Utils.GetXrefs(BASE_URL, ids, fout)

  elif args.op=='show_version':
    ensembl.Utils.ShowVersion(BASE_URL, fout)

  else:
    parser.error('Invalid operation: {0}'.format(args.op))

  logging.info(('%s: elapsed time: %s'%(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
