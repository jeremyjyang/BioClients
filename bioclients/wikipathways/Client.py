#!/usr/bin/env python3
##############################################################################
### wikipathways_utils.py - utility for Wikipathways REST API.
### See: http://www.wikipathways.org/index.php/Help:WikiPathways_Webservice/API
### Formats: xml, json
##############################################################################
import sys,os,re,argparse,time,logging
#
from .. import wikipathways
#
##############################################################################
if __name__=='__main__':
  OFMTS = ["gpml", "png", "svg", "pdf", "txt", "pwf", "owl"]
  API_HOST='webservice.wikipathways.org'
  API_BASE_PATH=''
  search_params = {'human':False}
  ops = ['list_organisms', 'list_pathways', 'get_pathway']
  parser = argparse.ArgumentParser(description='WikiPathways REST API client')
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--nchunk", type=int, default=None)
  parser.add_argument("--regex", help="regular expression query")
  parser.add_argument("--str_query", help="string query")
  parser.add_argument("--ofmt", choices=OFMTS, default="gpml", help="output pathway image format")
  parser.add_argument("--human", action="store_true", help="human only")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

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
  if len(ids)>0: logging.info('Input IDs: %d'%(len(ids)))

  api_base_url='https://'+args.api_host+args.api_base_path

  t0=time.time()

  if args.op=="list_organisms":
    wikipathways.ListOrganisms(api_base_url, fout)

  elif args.op=="list_pathways":
    wikipathways.ListPathways(api_base_url, search_params, fout)

  elif args.op=="get_pathway":
    wikipathways.GetPathway(api_base_url, ids, ofmt, fout)

  else:
    parser.error('Invalid operation: {0}'.format(args.op))

  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

