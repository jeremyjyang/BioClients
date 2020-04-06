#!/usr/bin/env python3
"""
See https://github.com/chembl/chembl_webresource_client
New with ChEMBL 25 March 2019:
https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
"""
###
import sys,os,argparse,logging
import csv

from chembl_webresource_client.new_client import new_client

NCHUNK = 50

#############################################################################
act_tags_selected = ['activity_id', 'assay_chembl_id', 'assay_type', 'src_id',
	'relation', 'standard_relation',
	'target_chembl_id', 'target_pref_name', 'target_organism', 'target_tax_id',
	'molecule_chembl_id', 'parent_molecule_chembl_id', 'molecule_pref_name',
	'canonical_smiles',
	'document_chembl_id', 'document_year',
	'pchembl_value', 'value', 'standard_value',
	'text_value', 'published_value',
	'units', 'qudt_units', 'uo_units', 'published_units', 'standard_units',
	'type', 'published_type', 'standard_type']
def CID2Activity(cids, args, fout):
  """
Compounds to targets through activities.
Normally select biochemical assays, protein targets, activities with pChembl.
Process in chunks to avoid timeouts due to size.
  """
  tags=None;
  n_act=0;
  i_start=(args.skip if args.skip else 0)
  i_end = min(args.nmax, len(cids)-i_start) if args.nmax else (len(cids)-i_start)
  writer = csv.writer(fout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
  for i in range(i_start, i_end, NCHUNK):
    if args.include_phenotypic:
      acts = new_client.activity.filter(molecule_chembl_id__in=cids[i:i+NCHUNK]).only(act_tags_selected)
    else:
      acts = new_client.activity.filter(molecule_chembl_id__in=cids[i:i+NCHUNK], pchembl_value__isnull=False).only(act_tags_selected)
    for act in acts:
      if not tags:
        tags = list(act.keys())
        writer.writerow(tags)
      writer.writerow([(act[tag] if tag in act else '') for tag in tags])
      n_act+=1
    logging.info('Progress: CIDs: %d / %d ; activities: %d'%(i-i_start, i_end-i_start, n_act))
  logging.info('Output activities: %d'%n_act)

#############################################################################
def TID2Targetcomponents(tids, args, fout):
  t_tags=['target_chembl_id','target_type','organism', 'species_group_flag', 'tax_id']
  tc_tags=['component_id','component_type','component_description','relationship', 'accession']
  ntc=0;
  writer = csv.writer(fout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
  for i in range(0, len(tids), NCHUNK):
    targets = new_client.target.filter(target_chembl_id__in=tids[i:i+NCHUNK])
    for t in targets:
      logging.debug('target tags: %s'%(str(t.keys())))
      logging.debug('target: %s'%(str(t)))
      t_vals=[(t[tag] if tag in t else '') for tag in t_tags]
      for tc in t['target_components']:
        if tc['component_type'] != 'PROTEIN':
          continue
        if ntc==0:
          writer.writerow(t_tags+tc_tags)
        tc_vals=[(tc[tag] if tag in tc else '') for tag in tc_tags]
        writer.writerow(t_vals+tc_vals)
        ntc+=1
  logging.info('Output target components (PROTEIN): %d'%ntc)

#############################################################################
def DID2Documents(dids, args, fout):
  d_tags=['document_chembl_id', 'doc_type', 'src_id', 'pubmed_id',
	'patent_id', 'doi', 'doi_chembl', 'year', 'journal', 'authors',
	'volume', 'issue', 'title', 'journal_full_title', 'abstract']
  ndoc=0;
  writer = csv.writer(fout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
  for i in range(0, len(dids), NCHUNK):
    documents = new_client.document.filter(document_chembl_id__in=dids[i:i+NCHUNK])
    for d in documents:
      logging.debug('document tags: %s'%(str(d.keys())))
      logging.debug('document: %s'%(str(d)))
      d_vals=[(d[tag] if tag in d else '') for tag in d_tags]
      if ndoc==0:
        writer.writerow(d_tags)
      writer.writerow(d_vals)
      ndoc+=1
  logging.info('Output documents: %d'%ndoc)

#############################################################################
def InchiKey2Molecule(inkeys, args, fout):
  m_tags=[
	'availability_type', 'biotherapeutic', 'black_box_warning', 'chebi_par_id', 
	'chirality', 'dosed_ingredient', 'first_approval', 'first_in_class', 
	'helm_notation', 'indication_class', 'inorganic_flag', 'max_phase', 
	'molecule_chembl_id', 'molecule_type', 'natural_product', 'oral', 
	'parenteral', 'polymer_flag', 'pref_name', 'prodrug', 'structure_type', 
	'therapeutic_flag', 'topical', 'usan_stem', 'usan_stem_definition', 
	'usan_substem', 'usan_year', 'withdrawn_class', 'withdrawn_country', 
	'withdrawn_flag', 'withdrawn_reason', 'withdrawn_year']
  n_mol=0;
  writer = csv.writer(fout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
  for i in range(0, len(inkeys), NCHUNK):
    mol = new_client.molecule
    mols = mol.get(inkeys[i:i+NCHUNK])
    for ii,m in enumerate(mols):
      inkey = inkeys[i+ii]
      logging.debug('mol tags: %s'%(str(m.keys())))
      logging.debug('mol: %s'%(str(m)))
      m_vals=[inkey]+[(m[tag] if tag in m else '') for tag in m_tags]
      if n_mol==0:
        writer.writerow(['inchikey']+m_tags)
      writer.writerow(m_vals)
      n_mol+=1
  logging.info('Output mols: %d'%n_mol)

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='ChEMBL REST API client: lookup by IDs')
  ops = ['cid2Activity', 'tid2Targetcomponents', 'did2Documents', 'inchikey2Mol']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--ids", help="input IDs, comma-separated")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int)
  parser.add_argument("--nmax", type=int)
  parser.add_argument("--include_phenotypic", action="store_true", help="else pChembl required")
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if not (args.ifile or args.id):
    parser.error('--i or --id required.')
  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

  ids=[]
  if args.ifile:
    with open(args.ifile, 'r') as fin:
      reader = csv.reader(fin, delimiter='\t')
      for row in reader:
        ids.append(row[0])
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  logging.info('Input IDs: %d'%len(ids))

  if args.op == 'cid2Activity':
    CID2Activity(ids, args, fout)
 
  elif args.op == 'inchikey2Mol':
    InchiKey2Molecule(ids, args, fout)
 
  elif args.op == 'tid2Targetcomponents':
    TID2Targetcomponents(ids, args, fout)
 
  elif args.op == 'did2Documents':
    DID2Documents(ids, args, fout)
 
