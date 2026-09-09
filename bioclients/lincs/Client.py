#!/usr/bin/env python3
"""
LINCS REST API client
New (2019) iLINCS: 
http://www.ilincs.org/ilincs/APIinfo
http://www.ilincs.org/ilincs/APIdocumentation
(http://lincsportal.ccs.miami.edu/dcic/api/ DEPRECATED?)
"""
###
import sys,os,argparse,re,time,json,logging
#
from .. import lincs
#
#############################################################################
if __name__=='__main__':
  epilog="""\
Examples:
NCBI Gene IDs: 207;
PerturbagenIDs: BRD-A00100033 (get_compound);
LINCS PertIDs: LSM-2121;
Perturbagen-Compound IDs: LSM-2421;
Signature IDs: LINCSCP_10260,LINCSCP_10261,LINCSCP_10262;
Dataset IDs: EDS-1013,EDS-1014;
Search Terms: cancer, vorinostat, MCF7.
"""
  parser = argparse.ArgumentParser(description=f'LINCS REST API client ({lincs.API_HOST})', epilog=epilog)
  ops = [
	'get_gene', 'get_compound', 'get_dataset',
	'list_genes', 'list_compounds', 'list_datasets',
	'search_dataset', 'search_signature',
	'get_signature'
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ids", help="input IDs, comma-separated")
  parser.add_argument("--searchTerm", dest="searchTerm", help="Entity searchTerm e.g. Rock1)")
  parser.add_argument("--lincs_only", action="store_true", help="LINCS datasets only")
  parser.add_argument("--ngene", type=int, default=50, help="top genes per signature")
  parser.add_argument("--nmax", type=int, help="max results")
  parser.add_argument("--skip", type=int, help="skip results")
  parser.add_argument("--api_host", default=lincs.API_HOST)
  parser.add_argument("--api_base_path", default=lincs.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  if args.op == 'get_gene':
    lincs.GetGene(ids, base_url, fout)

  elif args.op == 'get_compound':
    lincs.GetCompound(ids, base_url, fout)

  elif args.op == 'list_compounds':
    lincs.ListCompounds(base_url, fout)

  elif args.op == 'get_dataset':
    lincs.GetDataset(ids, base_url, fout)

  elif args.op == 'search_dataset':
    lincs.SearchDataset(args.searchTerm, args.lincs_only, base_url, fout)

  elif args.op == 'search_signature':
    lincs.SearchSignature(ids, args.lincs_only, base_url, fout)

  elif args.op == 'get_signature':
    lincs.GetSignature(ids, args.ngene, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')

