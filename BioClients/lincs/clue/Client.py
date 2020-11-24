#!/usr/bin/env python3
#############################################################################
### CMap Clue API client.
### CMap is the project; Clue is the platform.
### https://clue.io/api
### https://clue.io/connectopedia/query_api_tutorial
### https://clue.io/connectopedia/perturbagen_types_and_controls
### l1000_type: "landmark"|"inferred"|"best inferred"|"not inferred"
### BING = Best inferred plus Landmark
### API services: cells, genes, perts, pcls, plates, profiles, sigs,
### probeset_to_entrez_id, rep_fda_exclusivity
#############################################################################
### Apps:
### https://clue.io/cell-app
### https://clue.io/repurposing-app
#############################################################################
### curl -X GET --header "user_key: YOUR_KEY_HERE" 'https://api.clue.io/api/cells?filter=\{"where":\{"provider_name":"ATCC"\}\}' |python3 -m json.tool
#############################################################################
import sys,os,re,argparse,json,logging
#
from ... import lincs
from ...util import yaml as util_yaml
#
#############################################################################
if __name__=="__main__":
  epilog='''\
CMap is the project; Clue is the platform.
https://clue.io/api. 
Credentials config file should be at $HOME/.clueapi.yaml.
'''
  parser = argparse.ArgumentParser(description='CLUE.IO REST API client utility', epilog=epilog)
  ops = ['getGenes', 'listGenes', 'listGenes_landmark', 
	'getPerturbagens', 'listPerturbagens', 'listDrugs',
	'countSignatures', 'getSignatures',
	'getCells', 'listCells',
	'listPerturbagenClasses',
	'listDatasets', 'listDatatypes',
	'search']
  id_types = ['cell_id', 'pert_id', 'gene_symbol', 'entrez_id']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--id_type", choices=id_types, help='query ID or field type, e.g. gene_symbol')
  parser.add_argument("--clue_where", help="Clue API search where, e.g. '{\"pert_desc\":\"sirolimus\",\"cell_id\":\"MCF7\"}'")
  parser.add_argument("--nmax", type=int, default=1000, help="max results")
  parser.add_argument("--skip", type=int, default=0, help="skip results")
  parser.add_argument("--api_host", default=lincs.clue.Utils.API_HOST)
  parser.add_argument("--api_base_path", default=lincs.clue.Utils.API_BASE_PATH)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.clueapi.yaml")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  params = util_yaml.ReadParamFile(args.param_file)

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  if args.ifile:
    fin = open(args.ifile)
    ids=[];
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
    logging.info('input queries: %d'%(len(ids)))
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op=='getGenes':
    if not ids: parser.error('--ids or --i required.')
    lincs.clue.Utils.GetGenes(params, ids, args.id_type, base_url, fout)

  elif args.op=='listGenes':
    lincs.clue.Utils.ListGenes(params, base_url, fout)

  elif args.op=='listGenes_landmark':
    lincs.clue.Utils.ListGenes_Landmark(params, base_url, fout)

  elif args.op=='getPerturbagens':
    if not ids: parser.error('--ids or --i required.')
    lincs.clue.Utils.GetPerturbagens(params, ids, args.id_type, base_url, fout)

  elif args.op=='listPerturbagens':
    lincs.clue.Utils.ListPerturbagens(params, base_url, fout)

  elif args.op=='listDrugs':
    lincs.clue.Utils.ListDrugs(params, base_url, fout)

  elif args.op=='getCells':
    if not ids: parser.error('--ids or --i required.')
    lincs.clue.Utils.GetCells(params, ids, args.id_type, base_url, fout)

  elif args.op=='listCells':
    lincs.clue.Utils.ListCells(params, base_url, fout)

  elif args.op=='getSignatures':
    if not args.clue_where: parser.error('--clue_where required.')
    lincs.clue.Utils.GetSignatures(params, args, base_url, fout)

  elif args.op=='countSignatures':
    if not args.clue_where: parser.error('--clue_where required.')
    lincs.clue.Utils.CountSignatures(params, args, base_url, fout)

  elif args.op=='listDatasets':
    lincs.clue.Utils.ListDatasets(params, base_url, fout)

  elif args.op=='listDatatypes':
    lincs.clue.Utils.ListDatatypes(params, base_url, fout)

  elif args.op=='listPerturbagenClasses':
    lincs.clue.Utils.ListPerturbagenClasses(params, base_url, fout)

  else:
    parser.error('Unsupported operation: %s'%args.op)
