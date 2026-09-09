#!/usr/bin/env python3
"""
Utility for STRING Db REST API.

STRING = Search Tool for the Retrieval of Interacting Genes/Proteins

See: http://string-db.org/help/api/

http://[database]/[access]/[format]/[request]?[parameter]=[value]

database:
string-db.org
string.embl.de
stitch.embl.de
"""
###
import sys,os,re,json,argparse,time,logging
#
from .. import stringdb
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='STRING-DB REST API client utility',
        epilog="""\
Example protein IDs: DRD1 DRD1_HUMAN DRD2 DRD2_HUMAN ;
Example species: 9606 (human, via taxon identifiers, http://www.uniprot.org/taxonomy) ;
Image formats: PNG|PNG_highres|SVG
""")
  ops = ['getIds', 'getInteractionPartners',
	'getNetwork', 'getNetworkImage',
	'getEnrichment', 'getPPIEnrichment', ]
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--id", dest="id", help="protein ID (ex:DRD1_HUMAN)")
  parser.add_argument("--ids", dest="ids", help="protein IDs, comma-separated")
  parser.add_argument("--idfile", dest="idfile", help="input file, protein IDs")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("--species", help="taxon code, ex: 9606 (human)")
  parser.add_argument("--minscore", type=int, default=500, help="signifcance threshold 0-1000")
  parser.add_argument("--limit", type=int, default=100, help="Max # interaction partners")
  parser.add_argument("--netflavor", choices=stringdb.NETWORK_FLAVORS, default='evidence', help="network flavor")
  parser.add_argument("--imgfmt", choices=stringdb.IMG_FMTS, default='image', help="image format")
  parser.add_argument("--api_host", default=stringdb.API_HOST)
  parser.add_argument("--api_base_path", default=stringdb.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  ids=[]
  if args.idfile:
    fin = open(args.idfile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())
  elif args.id:
    ids=[args.id]

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  if args.op == 'getIds':
    if not ids: parser.error('PID[s] required.')
    stringdb.GetIds(ids, base_url, fout)

  elif args.op == 'getInteractionPartners':
    if not ids: parser.error('ID[s] required.')
    stringdb.GetInteractionPartners(ids, args.species, args.limit, args.minscore, base_url, fout)

  elif args.op == 'getEnrichment':
    if not len(ids)>1: parser.error('IDs (2+) required.')
    stringdb.GetEnrichment(ids, args.species, args.minscore, base_url, fout)

  elif args.op == 'getPPIEnrichment':
    if not len(ids)>1: parser.error('IDs (2+) required.')
    stringdb.GetPPIEnrichment(ids, args.species, args.minscore, base_url, fout)

  elif args.op == 'getNetwork':
    if not ids: parser.error('ID required.')
    stringdb.GetNetwork(ids[0], args.species, args.minscore, args.netflavor, base_url, fout)

  elif args.op == 'getNetworkImage':
    if not ids: parser.error('ID required.')
    if not args.ofile: parser.error('--o OUTFILE required.')
    # Reopen file binary-mode:
    fout.close()
    fout = open(args.ofile, "wb+")
    stringdb.GetNetworkImage(ids[0], args.species, args.minscore, args.netflavor, args.imgfmt, base_url, fout)

  else:
    parser.print_help()

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

