#!/usr/bin/env python3
"""
Sparql endpoint client
"""
#############################################################################
import os,sys,json,argparse,re,time,logging

import SPARQLWrapper

from .. import sparql as util_sparql

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
  epilog = f"SPARQLWRAPPERVERSION: {SPARQLWrapper.__version__}"
  parser = argparse.ArgumentParser(description='Sparql utilities', epilog=epilog)
  ENDPOINT="http://dbpedia.org/sparql"
  OPERATIONS = ["query", "test", ]
  parser.add_argument("op", help="OPERATION")
  parser.add_argument("--rqfile", help="Sparql input file")
  parser.add_argument("--rq", help="Sparql input string")
  parser.add_argument("--o", dest="ofile", help="output results (TSV)")
  parser.add_argument("--endpoint", default=ENDPOINT, help=f"Sparql endpoint [{ENDPOINT}]")
  parser.add_argument("--defgraph", help="default graph URL")
  parser.add_argument("--nmax", type=int, default=1000, help="max returned triples")
  parser.add_argument("--fmt", choices=FMTS.keys(), default='JSON', help="output format")
  parser.add_argument("--test_drugname", default="metformin", help="test drugname query")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  t0=time.time()
  fout = open(args.ofile, 'w+') if args.ofile else sys.stdout

  logging.debug(f"SPARQLWrapper_Version: {SPARQLWrapper.__version__}")
  logging.debug(f"fmt: {args.fmt}")

  if args.op== "test":
    util_sparql.Test(args.test_drugname, FMTS[args.fmt])

  elif args.op== "query":
    if args.rqfile:
      with open(args.rqfile) as fin:
        rqcode = fin.read()
    elif args.rq:
      rqcode = args.rq
    else:
      parser.error("--rq or --rqfile required.")

    if args.fmt=='XML':
      results = util_sparql.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
      results = results.convert()
      fout.write(f"{results.toxml()}\n")
    elif args.fmt=='JSON':
      results = util_sparql.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
      results = results.convert()
      fout.write(json.dumps(results, indent=2)+"\n")
    elif args.fmt=='N3':
      results = util_sparql.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS[args.fmt])
      fout.write(results._convertN3()+"\n")
    elif args.fmt=='TSV':
      results = util_sparql.SparqlRequest(rqcode, args.endpoint, args.defgraph, FMTS['JSON'])
      results = results.convert()
      util_sparql.Results2TSV(results, [], nmax, fout)
    else:
      results = util_sparql.SparqlRequest(rqcode, args.endpoint, args.defgraph, None)
      fout.write(str(results)+"\n")

  else:
    parser.error(f"Unsupported operation: {args.op}")
