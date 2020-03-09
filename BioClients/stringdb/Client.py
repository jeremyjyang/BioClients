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
import urllib,urllib.request,urllib.parse
#
from ..util import rest_utils
#
API_HOST='string-db.org'
API_BASE_PATH='/api'
#
NETWORK_FLAVORS=['evidence','confidence','actions']
IMG_FMTS=['image','highres_image','svg']
#
##############################################################################
def GetIds(base_url, pids, fout):
  url=base_url+'/tsv/get_string_ids'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; results: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetInteractionPartners(base_url, pids, species, minscore, fout):
  url=base_url+'/tsv/interaction_partners'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; interaction partners: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetEnrichment(base_url, pids, species, minscore, fout):
  url=base_url+'/tsv/enrichment'
  url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('query genes: %d ; enrichment results: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetPPIEnrichment(base_url, pids, species, minscore, fout):
  url=base_url+'/tsv/ppi_enrichment'
  url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('query genes: %d ; enrichment results: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetNetwork(base_url, pid, species, minscore, netflavor, fout):
  """Format: PNG image."""
  url=base_url+'/tsv/network?identifier=%s'%(pid)
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  url+=('&network_flavor=%s'%netflavor)
  rval=rest_utils.GetURL(url, parse_json=False, parse_xml=False)
  fout.write(rval)
  logging.info('edges: %d'%(len(rval.splitlines())-1))

##############################################################################
def GetNetworkImage(base_url, pid, species, minscore, netflavor, imgfmt, fout):
  url=base_url+'/%s/network?identifier=%s'%(imgfmt, pid)
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  url+=('&network_flavor=%s'%netflavor)
  rval=rest_utils.GetURL(url, parse_json=False, parse_xml=False)
  fout.write(rval)

##############################################################################
def GetInteractors(base_url, pids, species, minscore, fout):
  """2018: May be deprecated since 2015."""
  url=base_url+'/tsv/interactors'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; interactors: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetActions(base_url, pids, species, minscore, fout):
  """2018: May be deprecated since 2015."""
  url=base_url+'/tsv/actions'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  url+=('&required_score=%d'%minscore)
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; actions: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
def GetAbstracts(base_url, pids, species, fout):
  """2018: May be deprecated since 2015."""
  url=base_url+'/tsv/abstracts'
  if len(pids)==1:
    url+=('?identifier=%s'%pids[0])
  else:
    url+=('?identifiers=%s'%urllib.parse.quote('\n'.join(pids)))
  url+=('&species=%s'%species if species else '')
  rval=rest_utils.GetURL(url, parse_xml=False, parse_json=False)
  fout.write(rval)
  logging.info('queries: %d ; abstracts: %d'%(len(pids), len(rval.splitlines())-1))

##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='STRING-DB REST API client utility',
        epilog="""\
Example protein IDs: DRD1 DRD1_HUMAN DRD2 DRD2_HUMAN ;
Example species: 9606 (human, via taxon identifiers, http://www.uniprot.org/taxonomy) ;
Image formats: PNG PNG_highres SVG ;
MAY BE DEPRECATED: getInteractors, getActions, getAbstracts
""")
  ops = ['getIds', 'getInteractionPartners',
	'getNetwork', 'getNetworkImage',
	'getEnrichment', 'getPPIEnrichment',
	'getInteractors', 'getActions', 'getAbstracts']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--id", dest="id", help="protein ID (ex:DRD1_HUMAN)")
  parser.add_argument("--ids", dest="ids", help="protein IDs, comma-separated")
  parser.add_argument("--idfile", dest="idfile", help="input file, protein IDs")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("--species", help="taxon code, ex: 9606 (human)")
  parser.add_argument("--minscore", type=int, default=500, help="signifcance threshold 0-1000")
  parser.add_argument("--netflavor", choices=NETWORK_FLAVORS, default='evidence', help="network flavor")
  parser.add_argument("--imgfmt", choices=IMG_FMTS, default='image', help="image format")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  pids=[]
  if args.idfile:
    fin=open(args.idfile)
    if not fin: parser.error('failed to open input file: %s'%args.idfile)
    while True:
      line=fin.readline()
      if not line: break
      pids.append(line.strip())
  elif args.ids:
    pids = re.split(r'\s*,\s*', args.ids.strip())
  elif args.id:
    pids=[args.id]

  if args.ofile:
    fout=open(args.ofile, "w+")
    if not fout: parser.error('failed to open output file: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.op == 'getIds':
    if not pids: parser.error('PID[s] required.')
    GetIds(base_url, pids, fout)

  elif args.op == 'getInteractors':
    if not pids: parser.error('PID[s] required.')
    GetInteractors(base_url, pids, args.species, args.minscore, fout)

  elif args.op == 'getInteractionPartners':
    if not pids: parser.error('PID[s] required.')
    GetInteractionPartners(base_url, pids, args.species, args.minscore, fout)

  elif args.op == 'getActions':
    if not pids: parser.error('PID[s] required.')
    GetActions(base_url, pids, args.species, args.minscore, fout)

  elif args.op == 'getEnrichment':
    if not len(pids)>1: parser.error('PIDs (2+) required.')
    GetEnrichment(base_url, pids, args.species, args.minscore, fout)

  elif args.op == 'getPPIEnrichment':
    if not len(pids)>1: parser.error('PIDs (2+) required.')
    GetPPIEnrichment(base_url, pids, args.species, args.minscore, fout)

  elif args.op == 'getAbstracts':
    if not pids: parser.error('PID[s] required.')
    GetAbstracts(base_url, pids, args.species, fout)

  elif args.op == 'getNetwork':
    if not pids: parser.error('PID required.')
    GetNetwork(base_url, pids[0], args.species, args.minscore, args.netflavor, fout)

  elif args.op == 'getNetworkImage':
    if not pids: parser.error('PID required.')
    if not args.ofile: parser.error('--o OUTFILE required.')
    fout.close()
    fout = open(args.ofile, "wb+") #binary
    if not fout: parser.error('failed to open output file: %s'%args.ofile)
    GetNetworkImage(base_url, pids[0], args.species, args.minscore, args.netflavor, args.imgfmt, fout)

  else:
    parser.print_help()

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

