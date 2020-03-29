#!/usr/bin/env python3
#############################################################################
### LINCS REST API client
### New (2019) iLINCS: 
### http://www.ilincs.org/ilincs/APIinfo
### http://www.ilincs.org/ilincs/APIdocumentation
#############################################################################
### (http://lincsportal.ccs.miami.edu/dcic/api/ DEPRECATED?)
#############################################################################
import sys,os,argparse,re,time,json,logging
#
from ..util import rest_utils
#
API_HOST="www.ilincs.org"
API_BASE_PATH="/api"
#
#############################################################################
def GeneInfo(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/GeneInfos/%s'%id_this
    rval = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def DatasetInfo(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/PublicDatasets/%s'%id_this
    rval = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def CompoundInfo(base_url, ids, fout):
  tags=None; n_cpd=0;
  for id_this in ids:
    url = base_url+'/Compounds/%s'%id_this
    cpds = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(cpds, indent=2))
    for cpd in cpds:
      if not tags:
        tags = [tag for tag in cpd.keys() if type(cpd[tag]) not in (list, dict)]
        fout.write('\t'.join(tags)+'\n')
      vals = [str(cpd[tag]) if tag in cpd else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_cpd+=1
  logging.info("IDs: {0}; n_cpd: {1}".format(len(ids), n_cpd))

#############################################################################
def SearchDatasets(base_url, searchTerm, lincs, fout):
  tags=None;
  url = base_url+'/PublicDatasets/findTermMeta'
  d = {'term':searchTerm}
  if lincs: d['lincs'] = True
  rval = rest_utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  dsets = rval['data'] if 'data' in rval else []
  for dset in dsets:
    logging.debug(json.dumps(dset, indent=2))
    if not tags:
      tags = [tag for tag in dset.keys() if type(dset[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(dset[tag]) if tag in dset else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("Datasets: {0}".format(len(dsets)))

#############################################################################
def SearchSignatures(base_url, ids, lincs, fout):
  #SignatureMeta?filter={"where":{"lincspertid":"LSM-2121"},"limit":10}
  tags=None; n_sig=0;
  for id_this in ids:
    url = base_url+'/SignatureMeta?filter={"where":{"lincspertid":"%s"}}'%id_this
    sigs = rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(sigs, indent=2))
    for sig in sigs:
      logging.debug(json.dumps(sig, indent=2))
      if not tags:
        tags = [tag for tag in sig.keys() if type(sig[tag]) not in (list, dict)]
        fout.write('\t'.join(tags)+'\n')
      vals = [str(sig[tag]) if tag in sig else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_sig+=1
  logging.info("IDs: {0}; n_sig: {1}".format(len(ids), n_sig))

#############################################################################
def GetSignatures(base_url, ids, ngene, fout):
  tags=None; n_gene=0;
  url = base_url+'/ilincsR/downloadSignature'
  d = {'sigID':(','.join(ids)), 'display':True, 'noOfTopGenes':ngene}
  rval = rest_utils.PostURL(url, data=d, parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  genes = rval['data']['signature'] if 'data' in rval and 'signature' in rval['data'] else []
  for gene in genes:
    logging.debug(json.dumps(gene, indent=2))
    if not tags:
      tags = [tag for tag in gene.keys() if type(gene[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(gene[tag]) if tag in gene else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_gene+=1
  logging.info("IDs: {0}; n_gene: {1}".format(len(ids), n_gene))

#############################################################################
if __name__=='__main__':
  epilog='''\
Examples:
NCBI Gene IDs: 207;
Perturbagen IDs: LSM-2121;
Perturbagen-Compound IDs: LSM-2421;
Signature IDs: LINCSCP_10260,LINCSCP_10261,LINCSCP_10262;
Dataset IDs: EDS-1013,EDS-1014;
Search Terms: cancer, vorinostat, MCF7.
'''
  parser = argparse.ArgumentParser(description='LINCS REST API client (%s)'%(API_HOST), epilog=epilog)
  ops = ['geneInfo', 'compoundInfo', 'perturbagenInfo', 'datasetInfo',
	'searchDatasets', 'searchSignatures',
	'getSignatures'
	]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ids", help="input IDs, comma-separated")
  parser.add_argument("--searchTerm", dest="searchTerm", help="Entity searchTerm e.g. Rock1)")
  parser.add_argument("--lincs", action="store_true", help="LINCS datasets only")
  parser.add_argument("--ngene", type=int, default=50, help="top genes per signature")
  parser.add_argument("--nmax", type=int, help="max results")
  parser.add_argument("--skip", type=int, help="skip results")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='http://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile,"w+")
    if not fout: parser.error('Cannot open: %s'%args.ofile)
  else:
    fout=sys.stdout

  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('Cannot open: %s'%args.ifile)
    ids=[]
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  if args.op == 'geneInfo':
    GeneInfo(base_url, ids, fout)

  elif args.op == 'compoundInfo':
    CompoundInfo(base_url, ids, fout)

  elif args.op == 'datasetInfo':
    DatasetInfo(base_url, ids, fout)

  elif args.op == 'searchDatasets':
    SearchDatasets(base_url, args.searchTerm, args.lincs, fout)

  elif args.op == 'searchSignatures':
    SearchSignatures(base_url, ids, args.lincs, fout)

  elif args.op == 'getSignatures':
    GetSignatures(base_url, ids, args.ngene, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

