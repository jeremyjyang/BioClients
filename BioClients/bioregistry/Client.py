#!/usr/bin/env python3
"""
Client for Bioregistry REST API.

See: https://bioregistry.io/apidocs/
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import bioregistry
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Bioregistry REST API client', epilog='')
  ops = [
	'list_collections', 
	'list_contexts', 
	'list_registry', 
	'list_metaregistry', 
	'list_contributors', 
	'get_reference', 
	]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input query IDs")
  parser.add_argument("--ids", help="input query IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--etype", default="", help="evidence codes (|-separated)")
  parser.add_argument("--prefix", help="CURIE prefix")
  parser.add_argument("--nchunk", type=int)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--api_host", default=bioregistry.API_HOST)
  parser.add_argument("--api_base_path", default=bioregistry.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = f"https://{args.api_host}{args.api_base_path}"

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  t0=time.time()

  if args.op =="list_contributors":
    bioregistry.ListEntities("contributors", base_url, fout)
  elif args.op =="list_collections":
    bioregistry.ListEntities("collections", base_url, fout)
  elif args.op =="list_contexts":
    bioregistry.ListEntities("contexts", base_url, fout)
  elif args.op =="list_metaregistry":
    bioregistry.ListEntities("metaregistry", base_url, fout)
  elif args.op =="list_registry":
    bioregistry.ListEntities("registry", base_url, fout)
  elif args.op =="get_reference":
    bioregistry.GetReference(ids, args.prefix, base_url, fout)

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
