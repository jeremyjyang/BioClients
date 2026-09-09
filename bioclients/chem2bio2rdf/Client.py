#!/usr/bin/env python3
"""
	Chem2Bio2RDF query utility.
	All relevant tables assumed to have substring "c2b2r_".
"""
import os,sys,argparse,re,time,logging

from .. import chem2bio2rdf as c2b2r

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Chem2Bio2RDF PostgreSql client utility")
  ops = [ "schema", "list_targets", "list_genes", "tablecounts", "get_target", "get_compound" ]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--tidfile", dest="tidfile", help="input TID file")
  parser.add_argument("--cidfile", dest="cidfile", help="input CID file")
  parser.add_argument("--tids", help="input TIDs (comma-separated)")
  parser.add_argument("--cids", help="input CIDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--schema_with", help="describe tables w/ SUBSTR in name")
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport", default="5432")
  parser.add_argument("--dbname")
  parser.add_argument("--dbschema", default="public")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.c2b2r.yaml")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  params = c2b2r.ReadParamFile(args.param_file)
  if args.dbhost: params['DBHOST'] = args.dbhost
  if args.dbport: params['DBPORT'] = args.dbport
  if args.dbname: params['DBNAME'] = args.dbname
  if args.dbusr: params['DBUSR'] = args.dbusr
  if args.dbpw: params['DBPW'] = args.dbpw

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

  dbcon = c2b2r.Connect(dbhost=params["DBHOST"], dbname=params["DBNAME"], dbusr=params["DBUSR"], dbpw=params["DBPW"])

  if args.op=="schema":
    c2b2r.DescribeSchema(dbcon, args.dbschema, args.schema_with)

  elif args.op=="tablecounts":
    c2b2r.DescribeCounts(dbcon)

  elif args.op=="get_target":
    c2b2r.GetTarget(dbcon, args.dbschema, tids,fout)

  elif args.op=="list_targets":
    c2b2r.ListTargets(dbcon, args.dbschema, fout)

  elif args.op=="list_genes":
    c2b2r.ListGenes(dbcon, args.dbschema, fout)

  elif args.op=="get_compound":
    fout.write('"cid"\t"synonyms"\t"isosmi"\n')
    n_found=0
    for cid in cids:
      ok=c2b2r.GetCompound(dbcon, args.dbschema, cid, fout)
      if ok: n_found+=1
      else: logging.info('CID %d not found'%(cid))
    fout.close()
    logging.info('%d / %d found'%(n_found, len(cids)))

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  dbcon.close()

