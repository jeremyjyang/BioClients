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
import sys,os,re,argparse,json,logging,yaml
import urllib.parse

from ..util import rest_utils

N_CHUNK=200

#############################################################################
def ListDatatypes(base_url, params):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = (base_url+'/dataTypes')
  response = rest_utils.GetURL(url, headers=headers, parse_json=True)
  logging.debug(json.dumps(response, indent=2))

#############################################################################
def ListDatasets(base_url, params):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url = (base_url+'/datasets')
  response = rest_utils.GetURL(url, headers=headers, parse_json=True)
  logging.debug(json.dumps(response, indent=2))

#############################################################################
def ListPerturbagenClasses(base_url, params, fout):
  headers = {"user_key":params['user_key']}
  url = (base_url+'/pcls')
  pcls = rest_utils.GetURL(url, headers=headers, parse_json=True)
  tags=None; n_pcl=0;
  for pcl in pcls:
    n_pcl+=1
    if not tags:
      tags=pcl.keys()
      fout.write('\t'.join(tags)+'\n')
    vals=[];
    for tag in tags:
      if tag not in pcl:
        vals.append('')
      else:
        vals.append(str(pcl[tag]))
    fout.write('\t'.join(vals)+'\n')
  logging.info('pcls: %d'%n_pcl)

#############################################################################
def GetGenes(base_url, params, ids, id_type, fout):
  url_base=(base_url+'/genes?user_key='+params['user_key'])
  tags = None
  n_gene=0;
  for id_this in ids:
    n_gene_this=0;
    logging.info('id: %s'%id_this)
    i_chunk=0;
    while True:
      qry=('{"where":{"%s":"%s"},"skip":%d,"limit":%d}'%(
	id_type, urllib.parse.quote(id_this), i_chunk*N_CHUNK, N_CHUNK))
      url=url_base+('&filter=%s'%(qry))
      try:
        genes = rest_utils.GetURL(url, parse_json=True)
      except:
        break
      if not genes:
        break
      for gene in genes:
        n_gene_this+=1
        if not tags:
          tags = gene.keys()
          fout.write('\t'.join(tags)+'\n')
        vals = []
        for tag in tags:
          if tag not in gene:
            vals.append('')
          elif type(gene[tag]) in (list, tuple):
            vals.append(';'.join([str(x) for x in gene[tag]]))
          else:
            vals.append(str(gene[tag]))
        fout.write('\t'.join(vals)+'\n')
      i_chunk+=1
    logging.info('\tgenes: %d'%n_gene_this)
    n_gene+=n_gene_this
  logging.info('genes: %d'%n_gene)

#############################################################################
def ListGenes_Landmark(base_url, params, fout):
  GetGenes(base_url, params, ['landmark'], 'l1000_type', fout)

#############################################################################
def ListGenes(base_url, params, fout):
  GetGenes(base_url, params, ['landmark', 'inferred', 'best inferred', 'not inferred'], 'l1000_type', fout)

#############################################################################
### pert_type:
###	trt_cp - Compound
###	trt_sh - shRNA for loss of function (LoF) of gene
###	trt_lig - Peptides and other biological agents (e.g. cytokine)
###	trt_sh.cgs - Consensus signature from shRNAs targeting the same gene
#############################################################################
def GetPerturbagens(base_url, params, ids, id_type, fout):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/perts')
  tags = None
  fields = ['pert_id', 'pert_iname', 'pert_type', 'pert_vendor', 'pert_url', 'id', 'pubchem_cid', 'entrez_geneId', 'vector_id', 'clone_name', 'oligo_seq', 'description', 'target', 'structure_url', 'moa', 'pcl_membership', 'tas', 'num_sig', 'status']
  n_pert=0;
  for id_this in ids:
    n_pert_this=0;
    logging.info('id: %s'%id_this)
    i_chunk=0;
    while True:
      qry = ('{"where":{"%s":"%s"},"fields":[%s],"skip":%d,"limit":%d}'%(
	id_type, urllib.parse.quote(id_this),
	(','.join(['"%s"'%f for f in fields])),
	i_chunk*N_CHUNK, N_CHUNK))
      url = url_base+('?filter=%s'%(qry))
      try:
        perts = rest_utils.GetURL(url, headers=headers, parse_json=True)
      except:
        continue
      if not perts:
        break
      logging.debug(json.dumps(perts, indent=2))
      for pert in perts:
        n_pert_this+=1
        if not tags:
          tags = pert.keys()
          fout.write('\t'.join(tags)+'\n')
        vals = []
        for tag in tags:
          if tag not in pert:
            vals.append('')
          elif type(pert[tag]) in (list, tuple):
            vals.append(';'.join([str(x) for x in pert[tag]]))
          else:
            vals.append(str(pert[tag]))
        fout.write('\t'.join(vals)+'\n')
      i_chunk+=1
    logging.info('\tperturbagens: %d'%n_pert_this)
    n_pert+=n_pert_this
  logging.info('perturbagens: %d'%n_pert)

#############################################################################
def ListPerturbagens(base_url, params, fout):
  pert_types = ['trt_cp', 'trt_lig', 'trt_sh', 'trt_sh.cgs', 'trt_oe', 'trt_oe.mut', 'trt_xpr', 'trt_sh.css', 'ctl_vehicle.cns', 'ctl_vehicle', 'ctl_vector', 'ctl_vector.cns', 'ctl_untrt.cns', 'ctl_untrt']
  GetPerturbagens(base_url, params, pert_types, 'pert_type', fout)

#############################################################################
def ListDrugs(base_url, params, fout):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/rep_drugs')
  tags = None
  n_drug=0; i_chunk=0;
  while True:
    qry = ('{"skip":%d,"limit":%d}'%(i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter=%s'%(qry))
    try:
      drugs = rest_utils.GetURL(url, headers=headers, parse_json=True)
    except Exception as e:
      logging.error('Exception: %s'%e)
      continue
    if not drugs:
      break
    for drug in drugs:
      n_drug+=1
      if not tags:
        tags = drug.keys()
        fout.write('\t'.join(tags)+'\n')
      vals = []
      for tag in tags:
        if tag not in drug:
          vals.append('')
        elif type(drug[tag]) in (list, tuple):
          vals.append(';'.join([str(x) for x in drug[tag]]))
        else:
          vals.append(str(drug[tag]))
      fout.write('\t'.join(vals)+'\n')
    i_chunk+=1
  logging.info('drugs: %d'%n_drug)

#############################################################################
def GetCells(base_url, params, ids, id_type, fout):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/cells')
  tags = None
  n_cell=0;
  for id_this in ids:
    n_cell_this=0;
    logging.info('id: %s'%id_this)
    i_chunk=0;
    while True:
      qry = ('{"where":{"%s":"%s"},"skip":%d,"limit":%d}'%(
	id_type, urllib.parse.quote(id_this),
	i_chunk*N_CHUNK, N_CHUNK))
      url = url_base+('?filter=%s'%(qry))
      try:
        cells = rest_utils.GetURL(url, headers=headers, parse_json=True)
      except:
        break
      if not cells:
        break
      logging.debug(json.dumps(cells, indent=2))
      for cell in cells:
        n_cell_this+=1
        if not tags:
          tags = cell.keys()
          fout.write('\t'.join(tags)+'\n')
        vals = []
        for tag in tags:
          if tag not in cell:
            vals.append('')
          elif type(cell[tag]) in (list, tuple):
            vals.append(';'.join([str(x) for x in cell[tag]]))
          else:
            vals.append(str(cell[tag]))
        fout.write('\t'.join(vals)+'\n')
      i_chunk+=1
    logging.info('\tcells: %d'%n_cell_this)
    n_cell+=n_cell_this
  logging.info('cells: %d'%n_cell)

#############################################################################
# 2570 (3/28/2019)
def ListCells(base_url, params, fout):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/cells')
  tags = None
  n_cell=0; i_chunk=0;
  while True:
    qry = ('{"skip":%d,"limit":%d}'%(i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter=%s'%(qry))
    try:
      cells = rest_utils.GetURL(url, headers=headers, parse_json=True)
    except Exception as e:
      logging.error('Exception: %s'%e)
      continue
    if not cells:
      break
    for cell in cells:
      n_cell+=1
      if not tags:
        tags = cell.keys()
        fout.write('\t'.join(tags)+'\n')
      vals = []
      for tag in tags:
        if tag not in cell:
          vals.append('')
        elif type(cell[tag]) in (list, tuple):
          vals.append(';'.join([str(x) for x in cell[tag]]))
        else:
          vals.append(str(cell[tag]))
      fout.write('\t'.join(vals)+'\n')
    i_chunk+=1
  logging.info('cells: %d'%n_cell)

#############################################################################
def CountSignatures(base_url, params, args):
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/sigs/count')
  url = url_base+('?where=%s'%(args.clue_where))
  try:
    sigs = rest_utils.GetURL(url, headers=headers, parse_json=True)
    logging.info('signatures: %d'%len(sigs))
  except Exception as e:
    logging.error('%s'%e)

#############################################################################
def GetSignatures(base_url, params, args, fout):
  fields = ['pert_id','pert_iname','pert_desc','pert_dose','cell_id','provenance_code','target_seq','target_is_lm','target_is_bing','target_zs','dn100_bing','up100_bing']
  headers = {"Accept":"application/json", "user_key":params['user_key']}
  url_base = (base_url+'/sigs')
  tags=None; n_sig=0; i_chunk=0;
  while True:
    qry = ('{"where":%s,"fields":[%s],"skip":%d,"limit":%d}'%(
	args.clue_where, (','.join(['"%s"'%f for f in fields])),
	args.skip+i_chunk*N_CHUNK, N_CHUNK))
    url = url_base+('?filter=%s'%(qry))
    try:
      sigs = rest_utils.GetURL(url, headers=headers, parse_json=True)
    except:
      continue
    if not sigs:
      break
    logging.debug(json.dumps(sigs, indent=2))
    for sig in sigs:
      n_sig+=1
      if not tags:
        tags = sig.keys()
        fout.write('\t'.join(tags)+'\n')
      vals = []
      for tag in tags:
        if tag not in sig:
          vals.append('')
        elif type(sig[tag]) in (list, tuple):
          vals.append(';'.join([str(x) for x in sig[tag]]))
        else:
          vals.append(str(sig[tag]))
      fout.write('\t'.join(vals)+'\n')
      if n_sig>=args.nmax: break
    if n_sig>=args.nmax: break
    i_chunk+=1
  logging.info('signatures: %d'%n_sig)

#############################################################################
if __name__=="__main__":
  API_HOST = "api.clue.io"
  API_BASE_PATH = "/api"

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
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--id_type", choices=id_types, help='query ID or field type, e.g. gene_symbol')
  parser.add_argument("--clue_where", help="Clue API search where, e.g. '{\"pert_desc\":\"sirolimus\",\"cell_id\":\"MCF7\"}'")
  parser.add_argument("--nmax", type=int, default=1000, help="max results")
  parser.add_argument("--skip", type=int, default=0, help="skip results")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.clueapi.yaml")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)

  args = parser.parse_args()

  with open(args.param_file, 'r') as fh:
    params = {}
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w+")
    if not fout: parser.error('Cannot open: %s'%args.ofile)
  else:
    fout = sys.stdout

  if args.ifile:
    fin = open(args.ifile)
    if not fin: parser.error('Cannot open: %s'%args.ifile)
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
    GetGenes(base_url, params, ids, args.id_type, fout)

  elif args.op=='listGenes':
    ListGenes(base_url, params, fout)

  elif args.op=='listGenes_landmark':
    ListGenes_Landmark(base_url, params, fout)

  elif args.op=='getPerturbagens':
    if not ids: parser.error('--ids or --i required.')
    GetPerturbagens(base_url, params, ids, args.id_type, fout)

  elif args.op=='listPerturbagens':
    ListPerturbagens(base_url, params, fout)

  elif args.op=='listDrugs':
    ListDrugs(base_url, params, fout)

  elif args.op=='getCells':
    if not ids: parser.error('--ids or --i required.')
    GetCells(base_url, params, ids, args.id_type, fout)

  elif args.op=='listCells':
    ListCells(base_url, params, fout)

  elif args.op=='getSignatures':
    if not args.clue_where: parser.error('--clue_where required.')
    GetSignatures(base_url, params, args, fout)

  elif args.op=='countSignatures':
    if not args.clue_where: parser.error('--clue_where required.')
    CountSignatures(base_url, params, args)

  elif args.op=='listDatasets':
    ListDatasets(base_url, params)

  elif args.op=='listDatatypes':
    ListDatatypes(base_url, params)

  elif args.op=='listPerturbagenClasses':
    ListPerturbagenClasses(base_url, params, fout)

  else:
    parser.error('Unsupported operation: %s'%args.op)
    parser.print_help()
