#!/usr/bin/env python3
"""
Pharos GraphQL API client
https://pharos.nih.gov/api
"""
###
import sys,os,argparse,json,re,time,logging
#
from ... import idg
#
#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Pharos GraphQL API client')
  ops = [
	'get_targets',
	'get_diseases',
	'test' ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file, target IDs")
  parser.add_argument("--ids", dest="ids", help="IDs, target, comma-separated")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idtype_target", choices=list(idg.pharos.Utils.IDTYPES_TARGET.keys()), default='sym', help="target ID type")
  parser.add_argument("--idtype_disease", choices=list(idg.pharos.Utils.IDTYPES_DISEASE.keys()), default='name', help="disease ID type")
  parser.add_argument("--nmax", type=int, help="max to return")
  parser.add_argument("--api_endpoint", default=idg.pharos.Utils.API_ENDPOINT)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())
  logging.info(f"Input IDs: {len(ids)}")

  t0 = time.time()

  if re.match(r'^get_', args.op) and not ids:
    parser.error(f"{args.op} requires IDs.")

  if args.op=='get_targets':
    idg.pharos.Utils.GetTargets(ids, args.idtype_target, args.api_endpoint, fout)

  elif args.op=='get_diseases':
    idg.pharos.Utils.GetDiseases(ids, args.idtype_disease, args.api_endpoint, fout)

  elif args.op=='test':
    idg.pharos.Utils.Test(args.api_endpoint, fout)

  else:
    logging.error(f"Invalid operation: {args.op}")

  logging.info("Elapsed time: "+time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))
