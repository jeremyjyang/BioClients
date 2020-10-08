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
from ..util import rest
#
#############################################################################
def GetGene(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/GeneInfos/%s'%id_this
    rval = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def GetDataset(base_url, ids, fout):
  tags=None;
  for id_this in ids:
    url = base_url+'/PublicDatasets/%s'%id_this
    rval = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2))
    if not tags:
      tags = [tag for tag in rval.keys() if type(rval[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(rval[tag]) if tag in rval else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
  logging.info("IDs: {0}".format(len(ids)))

#############################################################################
def GetCompound(base_url, ids, fout):
  tags=None; n_cpd=0;
  for id_this in ids:
    url = base_url+'/Compounds/%s'%id_this
    cpd = rest.Utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(cpd, indent=2))
    if not tags:
      tags = [tag for tag in cpd.keys() if type(cpd[tag]) not in (list, dict)]
      fout.write('\t'.join(tags)+'\n')
    vals = [str(cpd[tag]) if tag in cpd else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_cpd+=1
  logging.info("IDs: {0}; n_cpd: {1}".format(len(ids), n_cpd))

#############################################################################
def SearchDataset(base_url, searchTerm, lincs, fout):
  tags=None;
  url = base_url+'/PublicDatasets/findTermMeta'
  d = {'term':searchTerm}
  if lincs: d['lincs'] = True
  rval = rest.Utils.PostURL(url, data=d, parse_json=True)
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
def SearchSignature(base_url, ids, lincs, fout):
  #SignatureMeta?filter={"where":{"lincspertid":"LSM-2121"},"limit":10}
  tags=None; n_sig=0;
  for id_this in ids:
    url = base_url+'/SignatureMeta?filter={"where":{"lincspertid":"%s"}}'%id_this
    sigs = rest.Utils.GetURL(url, parse_json=True)
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
def GetSignature(base_url, ids, ngene, fout):
  tags=None; n_gene=0;
  url = base_url+'/ilincsR/downloadSignature'
  d = {'sigID':(','.join(ids)), 'display':True, 'noOfTopGenes':ngene}
  rval = rest.Utils.PostURL(url, data=d, parse_json=True)
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
  API_HOST="www.ilincs.org"
  API_BASE_PATH="/api"
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
  parser = argparse.ArgumentParser(description='LINCS REST API client (%s)'%(API_HOST), epilog=epilog)
  ops = ['get_gene', 'get_compound', 'get_dataset',
	'search_dataset', 'search_signature',
	'get_signature'
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

  base_url =' http://'+args.api_host+args.api_base_path

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
    lincs.Utils.GetGene(base_url, ids, fout)

  elif args.op == 'get_compound':
    lincs.Utils.GetCompound(base_url, ids, fout)

  elif args.op == 'get_dataset':
    lincs.Utils.GetDataset(base_url, ids, fout)

  elif args.op == 'search_datasets':
    lincs.Utils.SearchDataset(base_url, args.searchTerm, args.lincs, fout)

  elif args.op == 'search_signatures':
    lincs.Utils.SearchSignature(base_url, ids, args.lincs, fout)

  elif args.op == 'get_signature':
    lincs.Utils.GetSignature(base_url, ids, args.ngene, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

