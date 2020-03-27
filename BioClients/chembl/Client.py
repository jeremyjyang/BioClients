#!/usr/bin/env python3
##############################################################################
### utility for ChEMBL REST API.
##############################################################################
### Consider using package https://github.com/chembl/chembl_webresource_client.
##############################################################################
### https://www.ebi.ac.uk/chembl/api/data/docs
### https://www.ebi.ac.uk/chembl/api/utils/docs
### https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions
### https://www.ebi.ac.uk/chembl/faq
##############################################################################
# ASSAY TYPES:
# Binding (assay_type=B) - Data measuring binding of compound to a molecular target, e.g. Ki, IC50, Kd.
# Functional (assay_type=F) - Data measuring the biological effect of a compound, e.g. %cell death in a cell line, rat weight.
# ADMET (assay_type=A) - ADME data e.g. t1/2, oral bioavailability.
# Toxicity (assay_type=T) - Data measuring toxicity of a compound, e.g., cytotoxicity.
# Physicochemical (assay_type=P) - Assays measuring physicochemical properties of the compounds in the absence of biological material e.g., chemical stability, solubility.
# Unclassified (assay_type=U) - A small proportion of assays cannot be classified into one of the above categories e.g., ratio of binding vs efficacy.
##############################################################################
import sys,os,re,json,argparse,time,logging
#
from .. import chembl
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/chembl/api/data'
#
##############################################################################
if __name__=='__main__':
  assay_types = {'B':'Binding', 'F':'Functional', 'A':'ADMET', 'T':'Toxicity', 'P':'Physicochemical', 'U':'Unclassified'}
  epilog='''Assay types: {0}. Example IDs: CHEMBL2 (compound); CHEMBL1642 (compound & drug); CHEMBL240  (target); CHEMBL1824  (target); CHEMBL1217643 (assay); CHEMBL3215220 (assay, PubChem assay 519, NMMLSC FPR); Q12809 (Uniprot)'''.format(str(assay_types))
  parser = argparse.ArgumentParser(description='ChEMBL REST API client', epilog=epilog)
  ops = ["status", "list_sources", "list_targets", "list_assays", "list_docs",
"list_mols", "list_drugs", "list_tissues", "list_cells", "list_mechanisms",
"search_assays", "get_mol",
"get_tgt", "get_assay", "getActivityForMol", "getActivityForAssay", "getActivityForTarget", "get_doc"]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="input IDs (mol, assay, target, or document)")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--uniprot" , help="UniProt accession ID")
  parser.add_argument("--assay_source" , help="source_id")
  parser.add_argument("--assay_type" , help="{0}".format(str(assay_types)))
  parser.add_argument("--pmin", type=float, help="min pChEMBL activity value (9 ~ 1nM *C50)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--include_phenotypic", action="store_true", help="else pChembl required")
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

  ids=[]
  if args.ifile:
    fin=open(args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  elif args.uniprot:
    ids = chembl.Utils.Uniprot2ID(args.uniprot, base_url)

  if args.op[:3]=="get" and not (args.ifile or args.ids):
    parser.error('--i or --ids required for operation {0}.'.format(args.op))

  if args.op == "status":
    api_ver,db_ver,status = chembl.Utils.Status(base_url)
    print('%s, %s, %s'%(api_ver, db_ver, status))

  elif args.op == "list_sources":
    chembl.Utils.ListSources(args.api_host, args.api_base_path, fout)

  elif args.op == "list_targets":
    chembl.Utils.ListTargets(args.api_host, args.api_base_path, args.skip, args.nmax, fout)

  elif args.op == "list_mols":
    chembl.Utils.ListMolecules(args.api_host, args.api_base_path, False, args.skip, args.nmax, fout)

  elif args.op == "list_drugs":
    chembl.Utils.ListMolecules(args.api_host, args.api_base_path, True, args.skip, args.nmax, fout)

  elif args.op == "list_docs":
    chembl.Utils.ListDocuments(args.api_host, args.api_base_path, args.skip, args.nmax, fout)

  elif args.op == "list_cells":
    chembl.Utils.ListCellLines(args.api_host, args.api_base_path, fout)

  elif args.op == "list_tissues":
    chembl.Utils.ListTissues(args.api_host, args.api_base_path, fout)

  elif args.op == "list_mechanisms":
    chembl.Utils.ListMechanisms(args.api_host, args.api_base_path, fout)

  elif args.op == "list_assays":
    chembl.Utils.ListAssays(args.api_host, args.api_base_path, args.skip, args.nmax, fout)

  elif args.op == "get_assay":
    chembl.Utils.GetAssay(base_url, ids, fout)

  elif args.op == "get_mol":
    chembl.Utils.GetMolecule(base_url, ids, fout)

  elif args.op == "getActivityForMol":
    chembl.Utils.GetActivity(ids, 'molecule', args.api_host, args.api_base_path, pmin, fout)

  elif args.op == "getActivityForAssay":
    chembl.Utils.GetActivity(ids, 'assay', args.api_host, args.pmin, fout)

  elif args.op == "getActivityForTarget":
    chembl.Utils.GetActivity(ids, 'target', args.api_host, args.pmin, fout)

  elif args.op == "get_tgt":
    chembl.Utils.GetTarget(ids, base_url, fout)

  elif args.op == "get_doc":
    chembl.Utils.GetDocument(ids, base_url, fout)

  elif args.op == "search_assays":
    if not (args.assay_source or args.assay_type): parser.error('--assay_source and/or --assay_type required.')
    if args.assay_type and args.assay_type[0].upper() not in ('B', 'F', 'P', 'A', 'U'):
      parser.error('Invalid assay type: {0}'.format(args.assay_type))
    chembl.Utils.SearchAssays(args.assay_source, args.assay_type, args.api_host, args.api_base_path, args.skip, args.nmax, fout)

  else:
    parser.error('No operation specified.')