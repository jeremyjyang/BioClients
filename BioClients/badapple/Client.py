#!/usr/bin/env python3
"""
    https://chiltepin.health.unm.edu/badapple2/apidocs/
"""
###
import sys,os,re,argparse,time,logging
#
from .. import badapple
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='Badapple REST API client utility',
        epilog="""\
Example SMILES: OC(=O)C1=C2CCCC(C=C3C=CC(=O)C=C3)=C2NC2=CC=CC=C12
Example scaffold IDs: 46,50
""")
  ops = ['get_compound2scaffolds', 'get_scaffold_info', 'get_scaffold2compounds', 'get_scaffold2drugs', ]
  parser.add_argument("op",choices=ops,help='OPERATION')
  parser.add_argument("--smi", dest="smi", help="input SMILES")
  parser.add_argument("--ids", dest="ids", help="input IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input SMILES file (with optional appended <space>NAME), or input IDs file")
  parser.add_argument("--db", choices=badapple.DATABASES, default="badapple2", help="default=badapple2")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--max_rings", type=int, default=10, help="max rings")
  parser.add_argument("--api_host", default=badapple.API_HOST)
  parser.add_argument("--api_base_path", default=badapple.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    fin = open(args.ifile)
    ids = [];
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    logging.info(f"Input SMILES: {len(ids)}")
    fin.close()
  elif args.ids:
    ids = re.split(r'[, ]+', args.ids.strip())
  elif args.smi:
    ids = [args.smi.strip()]

  if args.op == "get_compound2scaffolds":
    badapple.GetCompound2Scaffolds(ids, args.db, args.max_rings, base_url, fout)

  elif args.op == "get_scaffold_info":
    badapple.GetScaffoldInfo(ids, args.db, base_url, fout)

  elif args.op == "get_scaffold2compounds":
    badapple.GetScaffold2Compounds(ids, args.db, base_url, fout)

  elif args.op == "get_scaffold2drugs":
    badapple.GetScaffold2Drugs(ids, args.db, base_url, fout)

  elif args.op == "get_version":
    #badapple.GetVersion(args.db, base_url, fout)
    parser.error("Not implemented.")

  else:
    parser.error("No operation specified.")

  logging.info(f"elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")
