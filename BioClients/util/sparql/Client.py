#!/usr/bin/env python3
"""
Sparql endpoint client
"""
#############################################################################
import os,sys,json,argparse,re,time,logging

import SPARQLWrapper

from .. import sparql

FMTS={
	'JSON':SPARQLWrapper.Wrapper.JSON,
	'JSONLD':SPARQLWrapper.Wrapper.JSONLD,
	'XML':SPARQLWrapper.Wrapper.XML,
	'RDF':SPARQLWrapper.Wrapper.RDF,
	'RDFXML':SPARQLWrapper.Wrapper.RDFXML,
	'N3':SPARQLWrapper.Wrapper.N3,
	'TTL':SPARQLWrapper.Wrapper.TURTLE,
	'CSV':SPARQLWrapper.Wrapper.CSV,
	'TSV':SPARQLWrapper.Wrapper.TSV
	}

#############################################################################
if __name__=='__main__':
  epilog="SPARQLWRAPPERVERSION: {}".format(SPARQLWrapper.__version__)
  parser = argparse.ArgumentParser(description='Sparql utilities', epilog=epilog)
  endpoint="http://dbpedia.org/sparql"
  parser.add_argument("--rqfile", help="Sparql input file")
  parser.add_argument("--rq", help="Sparql input string")
  parser.add_argument("--o", dest="ofile", help="output results (TSV)")
  parser.add_argument("--endpoint", default=endpoint, help="Sparql endpoint")
  parser.add_argument("--defgraph", help="default graph URL")
  parser.add_argument("--nmax", type=int, default=1000, help="max returned triples")
  parser.add_argument("--fmt", choices=FMTS.keys(), default='JSON', help="output format")
  parser.add_argument("--test", action="store_true", help="test query")
  parser.add_argument("--test_drugname", default="metformin", help="test drugname query")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if args.test:
    sparql.Utils.Test(args.test_drugname, FMTS[args.fmt])
    sys.exit()

  if args.rqfile:
    with open(args.rqfile) as fin:
      rqcode = fin.read()
  elif args.rq:
    rqcode = args.rq
  else:
    parser.error("--rq or --rqfile required.")

  fout = open(args.ofile,'w+') if args.ofile else sys.stdout

  t0=time.time()

  logging.info('fmt: %s'%(args.fmt))

  if args.fmt=='XML':
    results = sparql.Utils.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
    results = results.convert()
    fout.write('%s\n'%results.toxml())

  elif args.fmt=='JSON':
    results = sparql.Utils.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
    results = results.convert()
    fout.write('%s\n'%json.dumps(results, indent=2))

  elif args.fmt=='N3':
    results = sparql.Utils.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
    fout.write('%s\n'%results._convertN3())

  elif args.fmt=='TSV':
    results = sparql.Utils.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS['JSON'])
    results = results.convert()
    sparql.Utils.Results2TSV(results, [], nmax, fout)

  else:
    results = sparql.Utils.SparqlRequest(rqcode, args.endpoint, args.defgraph, None)
    fout.write('%s\n'%str(results))


