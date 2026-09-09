#!/usr/bin/env python3
"""
Neo4j client (via py2neo API)
https://neo4j.com/docs/cypher-manual
https://py2neo.org
"""
#############################################################################
import sys,os,argparse,logging
import py2neo

from .. import neo4j as util_neo4j

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Neo4j client (via py2neo API)", epilog="See https://neo4j.com/docs/cypher-manual, https://py2neo.org.")
  ops = [ 'dbinfo', 'query', 'dbsummary' ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input query file (CQL aka Cypher)")
  parser.add_argument("--cql", help="input query (CQL aka Cypher)")
  parser.add_argument("--o", dest="ofile", help="output (TSV|JSON)")
  parser.add_argument("--ofmt", choices=('TSV', 'JSON'), default='TSV')
  parser.add_argument("--dbhost", default=util_neo4j.DBHOST)
  parser.add_argument("--dbport", type=int, default=util_neo4j.DBPORT)
  parser.add_argument("--dbscheme", default=util_neo4j.DBSCHEME)
  parser.add_argument("--dbusr", default=util_neo4j.DBUSR)
  parser.add_argument("--dbpw", default=util_neo4j.DBPW)
  parser.add_argument("--secure", action="store_true", help="secure connection (TLS)")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.op == 'dbinfo':
    db = util_neo4j.DbConnect(dbhost=args.dbhost, dbport=args.dbport, dbscheme=args.dbscheme, dbusr=args.dbusr, dbpw=args.dbpw, secure=args.secure)
    util_neo4j.DbInfo(db, fout)

  elif args.op == 'dbsummary':
    db = util_neo4j.DbConnect(dbhost=args.dbhost, dbport=args.dbport, dbscheme=args.dbscheme, dbusr=args.dbusr, dbpw=args.dbpw, secure=args.secure)
    util_neo4j.DbSummary(db, fout)

  elif args.op == 'query':
    db = util_neo4j.DbConnect(dbhost=args.dbhost, dbport=args.dbport, dbscheme=args.dbscheme, dbusr=args.dbusr, dbpw=args.dbpw, secure=args.secure)
    if args.ifile:
      fin = open(args.ifile)
      cql = fin.read()
    elif args.cql:
      cql = args.cql
    else:
      parser.error('--cql or --i required for query.')
    util_neo4j.DbQuery(db, cql, args.ofmt, fout)

  else:
    parser.error(f"Unsupported operation: {args.op}")
