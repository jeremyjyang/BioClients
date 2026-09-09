#!/usr/bin/env python3
"""
See http://www.guidetopharmacology.org/webServices.jsp
"""
import sys,os,re,argparse,time,logging,urllib.parse,json
#
from .. import iuphar
#
API_HOST='www.guidetopharmacology.org'
API_BASE_PATH='/services'
#
#############################################################################
if __name__=='__main__':
  SEARCH_TYPE='substructure'; 
  epilog='''\
operations:
  list_targets: list targets (selected by type, db, accessionId);
  list_target_families: list target families ;
  get_target: get target (requires ID);
  get_target_interactions: get target interactions (requires ID);
  get_target_dblinks: get target dblinks (requires ID);
  get_target_substrates: get target substrates (requires ID);
  get_target_function: get target function (requires ID);
  get_target_products: get target products (requires ID);
  get_target_gpinfo: get target gene protein info (requires ID);
  get_ligand_synonyms: get ligand synonyms (requires ID);
  list_ligands: list ligands (selected by type, db, accessionId);
  get_ligand: get ligand (requires ID);
  get_ligand_interactions: get ligand interactions (requires ID);
  get_ligand_dblinks: get ligand dblinks (requires ID);
  get_ligand_structure: get ligand structure (requires ID);
  get_target_synonyms: get target synonyms (requires ID);
  search_ligand: structure search (requires smiles query);
'''

  parser = argparse.ArgumentParser(description='IUPHAR/GuideToPharmacolog API client', epilog=epilog)
  ops=[ "list_targets", "list_target_families", "get_target", "get_target_interactions", "get_target_dblinks", "get_target_substrates", "get_target_function", "get_target_products", "get_target_gpinfo", "get_ligand_synonyms", "list_ligands", "get_ligand", "get_ligand_interactions", "get_ligand_dblinks", "get_ligand_structure", "get_target_synonyms", "search_ligand" ]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file of IDs (targetId|ligandId|accessionId)")
  parser.add_argument("--ids", help="ID list (comma-separated)(targetId|ligandId|accessionId)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--tgt_type", help="GPCR|NHR|LGIC|VGIC|OtherIC|Enzyme|CatalyticReceptor|Transporter|OtherProtein|AccessoryProtein")
  parser.add_argument("--lig_type", help="Synthetic organic|Metabolite|Natural product|Endogenous peptide|Peptide|Antibody|Inorganic|Approved|Withdrawn|Labelled|INN")
  parser.add_argument("--itr_type", help="Activator|Agonist|Allosteric modulator|Antagonist|Antibody|Channel blocker|Gating inhibitor|Inhibitor|Subunit-specific")
  parser.add_argument("--aff", type=float, help="affinity minimun")
  parser.add_argument("--aff_type", help="pA2|pEC50|pIC50|pKB|pKd|pKi")
  parser.add_argument("--smiles", help="structure search query")
  parser.add_argument("--search_type", help="substructure|exact|similarity")
  parser.add_argument("--species", help="Human|Mouse|Rat|etc.")
  parser.add_argument("--db", help="external accessionId database ChEMBL|EntrezGene|HGNC|PubChemCID|UniProt|etc.")
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

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids.strip())

  t0=time.time()

  if args.op == "list_targets":
    iuphar.ListTargets(BASE_URL, args.tgt_type, args.db, ids, fout)

  elif args.op == "list_target_families":
    iuphar.ListTargetFamilies(BASE_URL, args.tgt_type, fout)

  elif args.op == "get_target":
    iuphar.GetTarget(BASE_URL, ids, fout)

  elif args.op == "get_target_interactions":
    iuphar.GetInteractions(BASE_URL, 'targets', ids, args.species, args.itr_type, args.aff_type, args.aff, fout)

  elif args.op == "get_target_dblinks":
    iuphar.GetDblinks(BASE_URL, 'targets', ids, args.species, args.db, fout)

  elif args.op == "get_target_substrates":
    iuphar.GetTargetSubstrates(BASE_URL, ids, args.species, fout)

  elif args.op == "get_target_products":
    iuphar.GetTargetProducts(BASE_URL, ids, args.species, fout)

  elif args.op == "get_target_function":
    iuphar.GetTargetFunction(BASE_URL, ids, args.species, fout)

  elif args.op == "get_target_gpinfo":
    iuphar.GetTargetGeneProteinInfo(BASE_URL, ids, fout)

  elif args.op == "get_target_synonyms":
    iuphar.GetSynonyms(BASE_URL, 'targets', ids, fout)

  elif args.op == "list_ligands":
    iuphar.ListLigands(BASE_URL, args.lig_type, args.db, ids, fout)

  elif args.op == "get_ligand":
    iuphar.GetLigand(BASE_URL, ids, fout)

  elif args.op == "get_ligand_interactions":
    iuphar.GetInteractions(BASE_URL, 'ligands', ids, args.species, args.itr_type, args.aff_type, args.aff, fout)

  elif args.op == "get_ligand_dblinks":
    iuphar.GetDblinks(BASE_URL, 'ligands', ids, fout)

  elif args.op == "get_ligand_structure":
    iuphar.GetLigandStructure(BASE_URL, ids, fout)

  elif args.op == "get_ligand_synonyms":
    iuphar.GetSynonyms(BASE_URL, 'ligands', ids, fout)

  elif args.op == "search_ligand":
    if not (args.smiles and args.search_type):
      parser.error('--smiles and --search_type required.'+usage)
    iuphar.SearchLigand(BASE_URL, args.smiles, args.search_type, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)
      
  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))

