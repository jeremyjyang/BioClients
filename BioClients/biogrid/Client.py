#!/usr/bin/env python3
"""
Client for BioGRID REST API.

See: http://wiki.thebiogrid.org/doku.php/biogridrest

Formats: tab1, tab2, extendedTab2, count, json, jsonExtended

EXPERIMENTAL_SYSTEM
	"Affinity Capture-Luminescence"
	"Affinity Capture-MS"
	"Affinity Capture-Western"
	"Biochemical Activity"
	"Co-fractionation"
	"Co-localization"
	"FRET"
	"PCA"
	"Phenotypic Enhancement"
	"Phenotypic Suppression"
	"Protein-peptide"
	"Reconstituted Complex"
	"Synthetic Growth Defect"
	"Two-hybrid"
"""
###
import sys,os,re,json,argparse,time,yaml,logging
#
from .. import biogrid
from ..util import yaml as util_yaml
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='BioGrid REST API client', epilog='')
  ops = ['list_organisms', 'list_idtypes', 'get_interactions', 'search_interactions']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="query IDs (comma-separated)")
  parser.add_argument("--i", dest="ifile", help="input query IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--inc_interspecies", type=bool, help="include inter-species interactions")
  parser.add_argument("--inc_self", type=bool, help="include self-interactions")
  parser.add_argument("--inc_evidence", type=bool, help="include only ELIST evidence (else exclude)")
  parser.add_argument("--elist", default="", help="evidence codes (|-separated)")
  parser.add_argument("--addl_idtypes", default="", help="additional ID types (|-separated)")
  parser.add_argument("--human", type=bool, help="human-only")
  parser.add_argument("--rex")
  parser.add_argument("--str_query")
  parser.add_argument("--nchunk", type=int)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--api_host", default=biogrid.API_HOST)
  parser.add_argument("--api_base_path", default=biogrid.API_BASE_PATH)
  parser.add_argument("--api_key", help="has precedence over param_file")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.biogrid.yaml")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  params = util_yaml.ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key

  search_params = {
	'inc_interspecies': args.inc_interspecies,
	'inc_self': args.inc_self,
	'inc_evidence': args.inc_evidence,
	'elist': re.split('[|\s]+', args.elist.strip()),
	'addl_idtypes': re.split('[|\s]+', args.addl_idtypes.strip()),
	'human': args.human
	}

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = f"https://{args.api_host}{args.api_base_path}"

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  t0=time.time()

  if args.op =="list_organisms":
    biogrid.ListOrganisms(params, base_url, fout)

  elif args.op =="list_idtypes":
    biogrid.ListIdTypes(params, base_url, fout)

  elif args.op =="get_interactions":
    biogrid.GetInteractions(params, ids, base_url, fout)

  elif args.op =="search_interactions":
    biogrid.SearchInteractions(params, ids, search_params, base_url, fout)

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
