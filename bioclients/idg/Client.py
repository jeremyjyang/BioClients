#!/usr/bin/env python3
"""
Pharos  REST API client
https://pharos.nih.gov/idg/api/v1/targets(589)
"""
###
import sys,os,argparse,json,re,time,logging
#
from .. import idg
#
#############################################################################
if __name__=='__main__':
  API_HOST="pharos.nih.gov"
  API_BASE_PATH="/idg/api/v1"
  IDTYPES = ['IDG_TARGET_ID', 'UNIPROT', 'ENSP', 'GSYMB']
  parser = argparse.ArgumentParser(description='Pharos REST API client')
  ops = [ 'list_targets', 'list_ligands', 'list_diseases',
	'get_targets', 'get_targetProperties', 'search_targets' ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file, target IDs")
  parser.add_argument("--ids", dest="ids", help="IDs, target, comma-separated")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idtype", choices=IDTYPES, default='IDG_TARGET_ID', help="target ID type")
  parser.add_argument("--nmax", type=int, help="max to return")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'\s*,\s*',args.ids.strip())

  t0 = time.time()

  if re.match(r'^get_', args.op) and not ids:
    parser.error('{0} requires IDs.'.format(args.op))

  if args.op=='get_targets':
    idg.GetTargets(BASE_URL, ids, args.idtype, fout)

  elif args.op=='get_targetProperties':
    idg.GetTargetProperties(BASE_URL, ids, args.idtype, fout)

  elif args.op=='list_targets':
    idg.ListItems('targets', BASE_URL, fout)

  elif args.op=='list_diseases':
    idg.ListItems('diseases', BASE_URL, fout)

  elif args.op=='list_ligands':
    idg.ListItems('ligands', BASE_URL, fout)

  elif args.op=='search_targets':
    logging.error('Not implemented yet.')

  else:
    logging.error('Invalid operation: {0}'.format(args.op))

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
