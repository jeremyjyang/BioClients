#!/usr/bin/env python3
"""
	Chem2Bio2RDF query utility.
	All relevant tables assumed to have substring "c2b2r_".
"""
import os,sys,argparse,re,time,logging

from .. import chem2bio2rdf as c2b2r

#############################################################################
if __name__=='__main__':
  DBHOST="cheminfov.informatics.indiana.edu";
  DBNAME="chord"; DBSCHEMA="public";
  DBUSR="cicc3"; DBPW="";
  parser = argparse.ArgumentParser(description="Chem2Bio2RDF PostgreSql client utility")
  ops = [ "schema", "list_targets", "list_genes", "tablecounts", "get_target", "get_compound" ]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--tidfile", dest="tidfile", help="input TID file")
  parser.add_argument("--cidfile", dest="cidfile", help="input CID file")
  parser.add_argument("--tids", help="input TIDs (comma-separated)")
  parser.add_argument("--cids", help="input CIDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--schema_with", help="describe tables w/ SUBSTR in name")
  parser.add_argument("--dbhost", default=DBHOST)
  parser.add_argument("--dbname", default=DBNAME)
  parser.add_argument("--dbschema", default=DBSCHEMA)
  parser.add_argument("--dbusr", default=DBUSR)
  parser.add_argument("--dbpw", default=DBPW)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  tids=[]
  if args.tidfile:
    fin = open(args.tidfile)
    while True:
      line = fin.readline()
      if not line: break
      tids.append(line.strip())
  elif args.tids:
    tids = re.split(r'[,\s]+', args.tids)

  cids=[]
  if args.cidfile:
    fin = open(args.cidfile)
    while True:
      line = fin.readline()
      if not line: break
      cids.append(int(line.strip()))
  elif args.cids:
    cids = re.split(r'[,\s]+', args.cids)

  t0=time.time()

  dbcon = c2b2r.Utils.Connect(dbhost=args.dbhost, dbname=args.dbname, dbusr=args.dbusr, dbpw=args.dbpw)

  if args.op=="schema":
    c2b2r.Utils.DescribeSchema(dbcon, args.dbschema, args.schema_with)

  elif args.op=="tablecounts":
    c2b2r.Utils.DescribeCounts(dbcon, args.dbschema)

  elif args.op=="get_target":
    c2b2r.Utils.GetTarget(dbcon, args.dbschema, tids,fout)

  elif args.op=="list_targets":
    c2b2r.Utils.ListTargets(dbcon, args.dbschema, fout)

  elif args.op=="list_genes":
    c2b2r.Utils.ListGenes(dbcon, args.dbschema, fout)

  elif args.op=="get_compound":
    fout.write('"cid"\t"synonyms"\t"isosmi"\n')
    n_found=0
    for cid in cids:
      ok=c2b2r.Utils.GetCompound(dbcon, args.dbschema, cid, fout)
      if ok: n_found+=1
      else: logging.info('CID %d not found'%(cid))
    fout.close()
    logging.info('%d / %d found'%(n_found, len(cids)))

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  dbcon.close()

