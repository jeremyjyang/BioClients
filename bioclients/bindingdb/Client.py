#!/usr/bin/env python
#############################################################################
### BindingDb Utilities
### http://www.bindingdb.org/bind/BindingDBRESTfulAPI.jsp
### XML output only.
#############################################################################
import sys,os,re,argparse,time,logging
#
from .. import bindingdb
#
##############################################################################
if __name__=='__main__':
  epilog = "Example Uniprot IDs: P35355, Q8HZR1"
  API_HOST='www.bindingdb.org'
  API_BASE_PATH='/axis2/services/BDBService'
  ops = ["get_ligands_by_uniprot", "get_targets_by_compound"]
  parser = argparse.ArgumentParser( description='BindingDb REST API client', epilog=epilog)
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--i", dest="ifile", help="input file, Uniprot IDs")
  parser.add_argument("--ids", help="Uniprot IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--smiles", help="compound query")
  parser.add_argument("--ic50_max", type=int, default=100)
  parser.add_argument("--sim_min", type=float, default=0.85)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url='http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info('Input IDs: %d'%(len(ids)))

  if args.op=="get_ligands_by_uniprot":
    bindingdb.GetLigandsByUniprot(api_base_url, ids, args.ic50_max, fout)

  elif args.op=="get_targets_by_compound":
    bindingdb.GetTargetsByCompound(api_base_url, args.smiles, args.sim_min, fout)

  else:
    parser.error('Operation invalid: {}'.format(args.op))

  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

