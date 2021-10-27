#!/usr/bin/env python3
"""
Client to HumanBase REST API.
Genome-scale Integrated Analysis of gene Networks in Tissues
GIANT has moved to HumanBase (http://hb.flatironinstitute.org/).
GIANT tissue networks integrate 987 genome-scale datasets, encompassing
~38,000 conditions from ~14,000 publications and include both expression and
interaction measurements.
"""
import sys,os,re,numpy,json,argparse,logging
#
from ..util import rest
#
API_HOST='hb.flatironinstitute.org'
API_BASE_PATH='/api'
#
##############################################################################
def ListDatasets(base_url, fout):
  rval=rest.GetURL(base_url+'/datasets', parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  datasets = rval
  tags=[];
  tags_db=[];
  i_dataset=0;
  for dataset in datasets:
    i_dataset+=1
    if not tags:
      tags=dataset.keys()
      fout.write('%s\n'%('\t'.join(tags)))
    vals=[]
    for tag in tags:
      if tag in dataset:
        vals.append(str(dataset[tag]))
    fout.write('%s\n'%('\t'.join(vals)))
    logging.info('\t%s'%dataset)
  logging.info('n_dataset: %d'%len(datasets))

##############################################################################
def ListDatatypes(base_url, fout):
  rval=rest.GetURL(base_url+'/datatypes', parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  datatypes = rval
  tags=[];
  tags_db=[];
  i_datatype=0;
  for datatype in datatypes:
    i_datatype+=1
    if not tags:
      tags=datatype.keys()
      fout.write('%s\n'%('\t'.join(tags)))
    vals=[]
    for tag in tags:
      if tag in datatype:
        vals.append(str(datatype[tag]))
    fout.write('%s\n'%('\t'.join(vals)))
    logging.info('\t%s'%datatype)
  logging.info('n_datatype: %d'%len(datatypes))

##############################################################################
def ListTerms(base_url, fout):
  rval=rest.GetURL(base_url+'/terms', parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  terms = rval
  tags=[];
  tags_db=[];
  i_term=0;
  for term in terms:
    i_term+=1
    if not tags:
      tags=term.keys()
      fout.write('%s\n'%('\t'.join(tags)))
    vals=[]
    for tag in tags:
      if tag in term:
        vals.append(str(term[tag]))
    fout.write('%s\n'%('\t'.join(vals)))
    logging.info('\t%s'%term)
  logging.info('n_term: %d'%len(terms))

##############################################################################
def ListGenes(base_url, fout):
  rval=rest.GetURL(base_url+'/genes', parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  genes = rval
  for gene in genes:
    fout.write('%s\n'%gene)
    logging.info('\t%s'%gene)
  logging.info('n_gene: %d'%len(genes))

##############################################################################
def GetFuncNet(base_url, tissue, genes, maxsize, prior, minwt, fout):
  url=base_url+'/networks'
  d = {'tissue':tissue, 'genes':('+'.join(genes))}
  if prior: d['prior'] = prior
  if maxsize: d['size'] = maxsize
  rval=rest.PostURL(url,data=d,parse_json=True)

  if not rval: return
  logging.debug(json.dumps(rval,sort_keys=True,indent=2))
  fn = rval
  ver = fn['version'] if fn.has_key('version') else ''
  edges = fn['edges'] if fn.has_key('edges') else []
  nodes = set(genes)
  wts = []
  n_edge=0;
  for edge in edges:
    gene_from, gene_to, weight = edge['source'],edge['target'],edge['weight']
    wt = float(weight)
    if wt<minwt: continue
    fout.write('%s,%s,%.3f\n'%(gene_from, gene_to, wt))
    n_edge+=1
    nodes.add(edge['source'])
    nodes.add(edge['target'])
    wts.append(wt)
  logging.info('weight range: [%.4f,%.4f] ; median: %.4f'%(min(wts),max(wts), numpy.median(wts)))
  logging.info('n_gene: %d (includes query %d)'%(len(nodes),len(genes)))
  logging.info('n_edge: %d'%n_edge)

##############################################################################
def GetFuncNetEvidence(base_url, tissue, source, target, fout):
  url=base_url+'/networks/evidence'
  d = {'tissue':tissue, 'source':source, 'target':target }
  rval=rest.PostURL(url,data=d,parse_json=True)
  logging.debug(json.dumps(rval,sort_keys=True,indent=2))
  tags_dataset = ["dataset", "description", "posterior", "slug", "title", "urltype", "version"]
  fout.write(','.join(tags_dataset)+'\n')
  datasets = rval['datasets'] if rval.has_key('datasets') else []
  for dataset in datasets:
    vals=[]
    for tag in tags_dataset:
      val = dataset[tag] if dataset.has_key(tag) else ''
      vals.append(val)
    fout.write(','.join(vals)+'\n')

  datatypes = rval['datatypes'] if rval.has_key('datatypes') else []
  for datatype in datatypes:
    logging.info('datatype: %s (weight=%s)'%(datatype['name'],datatype['weight']))
 
##############################################################################
if __name__=='__main__':
  FN_SIZE=50; FN_PRIOR=0.1; FN_MIN=0.0; 
  epilog="""\
	--get_funcnet: functional network for tissue, 1+ gene[s];
	--get_evidence: FN evidence for tissue, 2 genes
"""

  parser = argparse.ArgumentParser(description='HumanBase API client; functional genomic networks', epilog=epilog)
  ops=['list_terms', 'list_datasets', 'list_datatypes', 'get_funcnet', 'get_evidence']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--tissue", help="(e.g. \"mammary_gland\")")
  parser.add_argument("--gene", help="(e.g. BRCA1)")
  parser.add_argument("--genes", help="gene list (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--funcnet_size", dest="fn_size", type=int, default=FN_SIZE, help="max genes beyond query")
  parser.add_argument("--funcnet_prior", dest="fn_prior", type=float, default=FN_PRIOR, help="prior probability")
  parser.add_argument("--funcnet_min", dest="fn_min", type=float, default=FN_MIN, help="min probability")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w+")
  else:
    fout = sys.stdout

  if args.genes:
    genes=re.split(r'[,\s]+', arg.genes.strip())
  elif args.gene:
    genes=[gene]

  if args.op == 'list_terms':
    ListTerms(BASE_URL, fout)

  elif args.op == 'list_datasets':
    ListDatasets(BASE_URL, fout)

  elif args.op == 'list_datatypes':
    ListDatatypes(BASE_URL, fout)

  elif args.op == 'get_funcnet':
    if not args.tissue and genes: parser.error('tissue and gene[s] required.')
    parser.error('not implemented yet.')
    #GetFuncNet(BASE_URL, args.tissue, genes, args.fn_size, args.fn_prior, args.fn_min, fout)

  elif args.op == 'get_evidence':
    if not args.tissue and genes: parser.error('tissue and gene[s] required.')
    parser.error('not implemented yet.')
    #GetFuncNetEvidence(BASE_URL, args.tissue, genes[0], genes[1], fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

