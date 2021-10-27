#!/usr/bin/env python3
"""
Utility for ChEMBL REST API.

Consider using package https://github.com/chembl/chembl_webresource_client.

* https://www.ebi.ac.uk/chembl/api/data/docs
* https://www.ebi.ac.uk/chembl/api/utils/docs
* https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions
* https://www.ebi.ac.uk/chembl/faq

ASSAY TYPES:
* Binding (assay_type=B) - Data measuring binding of compound to a molecular target, e.g. Ki, IC50, Kd.
* Functional (assay_type=F) - Data measuring the biological effect of a compound, e.g. %cell death in a cell line, rat weight.
* ADMET (assay_type=A) - ADME data e.g. t1/2, oral bioavailability.
* Toxicity (assay_type=T) - Data measuring toxicity of a compound, e.g., cytotoxicity.
* Physicochemical (assay_type=P) - Assays measuring physicochemical properties of the compounds in the absence of biological material e.g., chemical stability, solubility.
* Unclassified (assay_type=U) - A small proportion of assays cannot be classified into one of the above categories e.g., ratio of binding vs efficacy.

CONFIDENCE_SCORE DESCRIPTION
0 - Default value - Target assignment has yet to be curated
1 - Target assigned is non-molecular
3 - Target assigned is molecular non-protein target
4 - Multiple homologous protein targets may be assigned
5 - Multiple direct protein targets may be assigned
6 - Homologous protein complex subunits assigned
7 - Direct protein complex subunits assigned
8 - Homologous single protein target assigned
9 - Direct single protein target assigned

MOLECULE DEVELOPMENT PHASES:
0 - 
1 - 
2 - 
3 - 
4 - Approved drug?
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
from .. import chembl
#
##############################################################################
if __name__=='__main__':
  assay_types = {'B':'Binding', 'F':'Functional', 'A':'ADMET', 'T':'Toxicity', 'P':'Physicochemical', 'U':'Unclassified'}
  epilog='''Assay types: {0}. Example IDs: CHEMBL2 (compound); CHEMBL1642 (compound & drug); CHEMBL240  (target); CHEMBL1824  (target); CHEMBL1217643 (assay); CHEMBL3215220 (assay, PubChem assay 519, NMMLSC FPR); Q12809 (Uniprot)'''.format(str(assay_types))
  parser = argparse.ArgumentParser(description='ChEMBL REST API client', epilog=epilog)
  ops = ["status",
	"list_sources",
	"list_targets",
	"list_assays",
	"list_docs",
	"list_mols",
	"list_drugs",
	"list_drug_indications",
	"list_tissues",
	"list_cells",
	"list_mechanisms",
	"list_organisms",
	"list_protein_classes",
	"search_assays",
	"search_mols_by_name",
	"get_mol",
	"get_mol_by_inchikey",
	"get_target",
	"get_target_components",
	"get_target_by_uniprot",
	"get_assay",
	"get_activity_by_mol",
	"get_activity_by_assay",
	"get_activity_by_target",
	"get_activity_properties",
	"get_document"]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs (e.g. mol, assay, target, document)")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--dev_phase", type=int, choices=list(range(5)), default=None, help="molecule development phase")
  parser.add_argument("--assay_source", help="source_id")
  parser.add_argument("--assay_type", help="{0}".format(str(assay_types)))
  parser.add_argument("--pmin", type=float, help="min pChEMBL activity value (9 ~ 1nM *C50)")
  parser.add_argument("--include_phenotypic", action="store_true", help="else pChembl required")
  parser.add_argument("--api_host", default=chembl.API_HOST)
  parser.add_argument("--api_base_path", default=chembl.API_BASE_PATH)
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

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
  if len(ids)>0: logging.info(f"Input IDs: {len(ids)}")

  if args.op[:3]=="get" and not (args.ifile or args.ids):
    parser.error(f"--i or --ids required for operation {args.op}.")

  if args.op == "status":
    api_ver,db_ver,status = chembl.Status(base_url, fout)

  elif args.op == "list_sources":
    chembl.ListSources(args.api_host, args.api_base_path, fout)

  elif args.op == "list_mechanisms":
    chembl.ListMechanisms(args.api_host, args.api_base_path, fout)

  elif args.op == "list_organisms":
    chembl.ListOrganisms(args.api_host, args.api_base_path, fout)

  elif args.op == "list_protein_classes":
    chembl.ListProteinClasses(args.api_host, args.api_base_path, fout)

  elif args.op == "list_targets":
    chembl.ListTargets(args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "list_mols":
    chembl.ListMolecules(args.dev_phase, args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "list_drugs":
    chembl.ListDrugs(args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "list_drug_indications":
    chembl.ListDrugIndications(args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "list_docs":
    chembl.ListDocuments(args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "list_cells":
    chembl.ListCellLines(args.api_host, args.api_base_path, fout)

  elif args.op == "list_tissues":
    chembl.ListTissues(args.api_host, args.api_base_path, fout)

  elif args.op == "list_assays":
    chembl.ListAssays(args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "get_assay":
    chembl.GetAssay(ids, base_url, fout)

  elif args.op == "get_mol":
    chembl.GetMolecule(ids, base_url, fout)

  elif args.op == "get_mol_by_inchikey":
    chembl.GetMoleculeByInchikey(ids, base_url, fout)

  elif args.op == "get_activity_by_mol":
    chembl.GetActivity(ids, 'molecule', args.pmin, args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "get_activity_by_assay":
    chembl.GetActivity(ids, 'assay', args.pmin, args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "get_activity_by_target":
    chembl.GetActivity(ids, 'target', args.pmin, args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  elif args.op == "get_activity_properties":
    chembl.GetActivityProperties(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == "get_target":
    chembl.GetTarget(ids, base_url, fout)

  elif args.op == "get_target_components":
    chembl.GetTargetComponents(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == "get_target_by_uniprot":
    chembl.GetTargetByUniprot(ids, base_url, fout)

  elif args.op == "get_document":
    chembl.GetDocument(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == "search_mols_by_name":
    chembl.SearchMoleculeByName(ids, base_url, fout)

  elif args.op == "search_assays":
    if not (args.assay_source or args.assay_type): parser.error('--assay_source and/or --assay_type required.')
    if args.assay_type and args.assay_type[0].upper() not in ('B', 'F', 'P', 'A', 'U'):
      parser.error(f"Invalid assay type: {args.assay_type}")
    chembl.SearchAssays(args.assay_source, args.assay_type, args.skip, args.nmax, args.api_host, args.api_base_path, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
