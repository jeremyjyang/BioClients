#!/usr/bin/env python3
"""
 Online Mendelian Inheritance in Man,
 "An Online Catalog of Human Genes and Genetic Disorders"

 See: https://omim.org/help/api
 The OMIM API URLs are organized in a very simple fashion:
   /api/[handler]?[parameters]
   /api/[handler]/[component]?[parameters]
   /api/[handler]/[action]?[parameters]
 The handler refers to the data object, such as an entry or a clinical synopsis.

 Handlers: entry, clinicalSynopsis, geneMap, search, html, dump

 entry?mimNumber=100100&format=json&apiKey=...

 https://omim.org/downloads/1kweo1_nTfuTCiVRnANNGQ
"""
###
import sys,os,re,json,argparse,time,logging
import urllib,urllib.parse
#
from ..util import rest
#
API_HOST='api.omim.org'	#US
#API_HOST='api.europe.omim.org'	#Europe
API_BASE_PATH='/api'
API_KEY='1kweo1_nTfuTCiVRnANNGQ' #will expire on Nov. 19th, 2019.
#
##############################################################################
if __name__=='__main__':
  fields_allowed=['text', 'existflags', 'allelicVariantList', 'clinicalSynopsis', 'seeAlso', 'referenceList', 'geneMap', 'externalLinks', 'contributors', 'creationDate', 'editHistory', 'dates', 'all' ]
  epilog='''\
operations: {
        entry : "entry resource, fetch records",
        clinical : "clinicalSynopsis resource, fetch records",
        genemap : "geneMap resource, fetch records",
        search : "search via defined syntax, some/all fields" },
example searches: {
	"muscular AND dystrophy NOT duchenne",
	"(muscular AND dystrophy) OR (duchenne AND gene)",
	"Bombay syndrome" }
'''
  parser = argparse.ArgumentParser(
        description="OMIM API client (Online Mendelian Inheritance in Man)", epilog=epilog)
  ops = ['entry', 'clinical', 'genemap', 'search']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--o", dest="ofile", help="output (CSV|TSV)")
  parser.add_argument("--mims", help="MIM ID[s], comma-separated (e.g. 100100,100200)")
  parser.add_argument("--query", help="search query")
  parser.add_argument("--rawquery", help="search rawquery")
  parser.add_argument("--inc_fields", default="all",  help="specify fields, comma-separated, or 'all'")
  parser.add_argument("--fmt", default="json", choices=('json', 'xml', 'python'), help="output format")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_key", default=API_KEY)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  if args.mims:
    mim_vals = map(lambda n:int(n), re.split(',', args.mims))
  else:
    parser.error("--mims required.")

  fields_vals = re.split(',', args.inc_fields)

  if len(set(fields_vals) - set(fields_allowed))>0:
    parser.error('disallowed fields: %s'%str(set(fields_vals) - set(fields_allowed)))

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  API_BASE_URL='https://'+args.api_host+args.api_base_path
  url=API_BASE_URL

  url_params=('&include=%s'%args.inc_fields if args.inc_fields else '')
  url_params+=('&format=%s'%args.fmt)
  url_params+=('&apiKey=%s'%args.api_key)

  if args.op == 'entry':
    url=API_BASE_URL+'/entry?mimNumber=%s'%(','.join(map(lambda n:str(n), mim_vals)))+url_params
    rval=rest.GetURL(url, parse_json=True, verbose=args.verbose)
    fout.write(json.dumps(rval, sort_keys=True, indent=2))

  elif args.op == 'genemap':
    url=API_BASE_URL+'/geneMap?mimNumber=%s'%(','.join(map(lambda n:str(n), mim_vals)))+url_params
    rval=rest.GetURL(url, parse_json=True, verbose=args.verbose)
    fout.write(json.dumps(rval, sort_keys=True, indent=2))

  elif args.op == 'clinical':
    url=API_BASE_URL+'/clinicalSynopsis?mimNumber=%s'%(','.join(map(lambda n:str(n), mim_vals)))+url_params
    rval=rest.GetURL(url, parse_json=True, verbose=args.verbose)
    fout.write(json.dumps(rval, sort_keys=True, indent=2))

  elif args.op == 'search':
    url=API_BASE_URL+'/entry/search?search=%s'%(urllib.parse.quote(query))+url_params
    rval=rest.GetURL(url, parse_json=True)
    fout.write(json.dumps(rval, sort_keys=True, indent=2))

  elif args.op == 'rawquery':
    url=API_BASE_URL+rawquery
    rval=rest.GetURL(url, parse_json=True)
    fout.write(json.dumps(rval, sort_keys=True, indent=2))

  else:
    parser.error('Unknown operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
