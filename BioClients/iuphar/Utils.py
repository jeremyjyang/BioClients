#!/usr/bin/env python3
##############################################################################
### See http://www.guidetopharmacology.org/webServices.jsp
##############################################################################
import sys,os,re,time,logging,urllib.parse,json
#
from ..util import rest
#
INT_TAGS=[
	"interactionId",
	"targetId",
	"ligandAsTargetId",
	"targetSpecies",
	"primaryTarget",
	"targetBindingSite",
	"ligandId",
	"ligandContext",
	"endogenous",
	"type",
	"action",
	"actionComment",
	"selectivity",
	"concentrationRange",
	"affinity",
	"affinityType",
	"originalAffinity",
	"originalAffinityType",
	"originalAffinityRelation",
	"assayDescription",
	"assayConditions",
	"useDependent",
	"voltageDependent",
	"voltage",
	"physiologicalVoltage"
]
INT_REF_TAGS=[
	"referenceId",
	"pmid",
	"type",
	"title",
	"year",
	"volume",
	"issue",
	"pages",
	"articleTitle",
	"authors",
	"editors",
	"publisher",
	"publisherAddress",
	"pubStatus",
	"website",
	"doi",
	"url",
	"isbn",
	"patentNumber",
	"assignee",
	"accessDate",
	"modifyDate",
	"priorityDate",
	"publicationDate"
]
#############################################################################
def ListTargets(base_url, tgt_type, db, ids, fout):
  n_tgt=0; n_out=0; n_err=0;
  tags=None;
  url=base_url+'/targets?'
  if tgt_type: url+=('&type=%s'%urllib.parse.quote(tgt_type))
  if db: url+=('&database=%s'%(db))
  for id_this in ids:
    url_this = url+('&accession=%s'%(urllib.parse.quote(id_this)))
    rval=rest.GetURL(url_this, parse_json=True)
    tgts=rval
    for tgt in tgts:
      n_tgt+=1
      if n_tgt==1 or not tags:
        tags=sorted(tgt.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((tgt[tag]) if tag in tgt else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    
  #logging.info(json.dumps(rval, indent=2))
  logging.info('n_tgt: %d'%n_tgt)
  logging.info('n_out: %d'%n_out)

############################# ################################################
def ListTargetFamilies(base_url,  tgt_type, fout):
  n_fam=0; n_out=0; n_err=0;
  tags=None;
  url=base_url+'/targets/families'
  if tgt_type: url+=('?type=%s'%urllib.parse.quote(tgt_type))
  rval=rest.GetURL(url, parse_json=True)
  fams=rval
  for fam in fams:
    n_fam+=1
    if n_fam==1 or not tags:
      tags=sorted(fam.keys())
      fout.write(('\t'.join(tags))+'\n')
    vals=[]
    for tag in tags:
      vals.append((fam[tag]) if tag in fam else '')
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
    
  #logging.info(json.dumps(rval, indent=2))
  logging.info('n_fam: %d'%n_fam)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetTarget(base_url, ids, fout):
  n_qry=0; n_tgt=0; n_out=0; n_err=0;
  tags=None;
  for tid in ids:
    n_qry+=1
    url=base_url+'/targets/%s'%tid
    rval=rest.GetURL(url, parse_json=True)
    tgt=rval
    n_tgt+=1
    if n_tgt==1 or not tags:
      tags=sorted(tgt.keys())
      fout.write(('\t'.join(tags))+'\n')
    vals=[]
    for tag in tags:
      vals.append((tgt[tag]) if tag in tgt else '')
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_tgt: %d'%n_tgt)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetTargetSubstrates(base_url, ids, species, fout):
  n_qry=0; n_tsb=0; n_out=0; n_err=0;
  tags=None;
  for id_query in ids:
    n_qry+=1
    url=base_url+('/targets/%s/substrates'%id_query)
    if species: url+=('?species=%s'%urllib.parse.quote(species))
    rval=rest.GetURL(url, parse_json=True)
    tsbs=rval
    for tsb in tsbs:
      n_tsb+=1
      if n_tsb==1 or not tags:
        tags=sorted(tsb.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((tsb[tag]) if tag in tsb else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1

  logging.info('n_tsb: %d'%n_tsb)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetTargetProducts(base_url, ids, species, fout):
  n_qry=0; n_prd=0; n_out=0; n_err=0;
  tags=None;
  for id_query in ids:
    n_qry+=1
    url=base_url+('/targets/%s/products'%id_query)
    if species: url+=('?species=%s'%urllib.parse.quote(species))
    rval=rest.GetURL(url, parse_json=True)
    prds=rval
    for prd in prds:
      n_prd+=1
      if n_prd==1 or not tags:
        tags=sorted(prd.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((prd[tag]) if tag in prd else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1

  logging.info('n_prd: %d'%n_prd)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetTargetFunction(base_url, ids, species, fout):
  n_qry=0; n_fnc=0; n_out=0; n_err=0;
  tags=None;
  for id_query in ids:
    n_qry+=1
    url=base_url+('/targets/%s/function'%id_query)
    if species: url+=('?species=%s'%urllib.parse.quote(species))
    rval=rest.GetURL(url, parse_json=True)
    fncs=rval
    for fnc in fncs:
      n_fnc+=1
      if n_fnc==1 or not tags:
        tags=sorted(fnc.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((fnc[tag]) if tag in fnc else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1

  logging.info('n_fnc: %d'%n_fnc)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetTargetGeneProteinInfo(base_url, ids, fout):
  n_qry=0; n_gpi=0; n_out=0; n_err=0;
  tags=None;
  for tid in ids:
    n_qry+=1
    url=base_url+'/targets/%s/geneProteinInformation'%tid
    rval=rest.GetURL(url, parse_json=True)
    gpis=rval
    for gpi in gpis:
      n_gpi+=1
      if n_gpi==1 or not tags:
        tags=sorted(gpi.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((gpi[tag]) if tag in gpi else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1

  logging.info('n_gpi: %d'%n_gpi)
  logging.info('n_out: %d'%n_out)

#############################################################################
def ListLigands(base_url, lig_type, db, ids, fout):
  n_lig=0; n_out=0; n_err=0;
  tags=None;
  url=base_url+'/ligands?'
  if lig_type: url+=('&type=%s'%urllib.parse.quote(lig_type))
  if db: url+=('&database=%s'%(db))
  for id_this in ids:
    url_this = url+('&database=%s&accession=%s'%(db, urllib.parse.quote(id_this)))
    rval = rest.GetURL(url_this, parse_json=True)
    ligs=rval
    for lig in ligs:
      n_lig+=1
      if n_lig==1 or not tags:
        tags=sorted(lig.keys())
        fout.write(('\t'.join(tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((lig[tag]) if tag in lig else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    
  logging.info('n_lig: %d'%n_lig)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetLigand(base_url, ids, fout):
  n_qry=0; n_lig=0; n_out=0; n_err=0;
  tags=None;
  for lid in ids:
    n_qry+=1
    url=base_url+'/ligands/%s'%lid
    rval=rest.GetURL(url, parse_json=True)
    lig=rval
    n_lig+=1
    if n_lig==1 or not tags:
      tags=sorted(lig.keys())
      fout.write(('\t'.join(tags))+'\n')
    vals=[]
    for tag in tags:
      vals.append((lig[tag]) if tag in lig else '')
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_lig: %d'%n_lig)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetLigandStructure(base_url, ids, fout):
  '''Smiles backslashes may cause problems.'''
  n_qry=0; n_lig=0; n_out=0; n_err=0;
  tags=None;
  for lid in ids:
    n_qry+=1
    url=base_url+'/ligands/%s/structure'%lid
    rval=rest.GetURL(url, parse_json=True)
    lig=rval
    if not lig:
      logging.error('Not found: %s'%(url))
      n_err+=1
      continue
    n_lig+=1
    if n_lig==1 or not tags:
      tags=sorted(lig.keys())
      fout.write(('\t'.join(tags))+'\n')
    vals=[]
    for tag in tags:
      vals.append((lig[tag]) if tag in lig else '')
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_lig: %d'%n_lig)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def GetInteractions(base_url, resource, ids, species, itr_type, aff_type, aff, fout):
  '''Include first reference only.'''
  n_qry=0; n_itr=0; n_out=0; n_err=0;
  n_dpt=0;
  for id_query in ids:
    n_qry+=1
    url=base_url+('/%s/%s/interactions?'%(resource, id_query))
    if species: url+=('&species=%s'%urllib.parse.quote(species))
    if itr_type: url+=('&type=%s'%urllib.parse.quote(itr_type))
    if aff_type: url+=('&affinityType=%s'%urllib.parse.quote(aff_type))
    if aff: url+=('&affinity=%.2f'%aff)
    rval=rest.GetURL(url, parse_json=True)
    itrs=rval
    if not itrs or type(itrs) not in (list, tuple):
      logging.error('Not found: %s'%(url))
      n_err+=1
      continue
    for itr in itrs:
      n_itr+=1
      dpts = itr['dataPoints'] if 'dataPoints' in itr else []
      for dpt in dpts:
        n_dpt+=1
        if n_dpt==1:
          fout.write(('\t'.join(INT_TAGS+INT_REF_TAGS))+'\n')
        vals=[]
        for tag in INT_TAGS:
          vals.append((dpt[tag]) if tag in dpt else '')
        refs = dpt['refs'] if 'refs' in dpt else []
        if refs:
          for tag in INT_REF_TAGS:
            vals.append((refs[0][tag]) if tag in refs[0] else '')
        else:
          vals.extend(['' for tag in INT_REF_TAGS])
        fout.write(('\t'.join(vals))+'\n')
        n_out+=1

  logging.info('n_itr: %d'%n_itr)
  logging.info('n_dpt: %d'%n_dpt)
  logging.info('n_out: %d'%n_out)
  logging.info('n_err: %d'%n_err)

#############################################################################
def SearchLigand(base_url, smi, search_type, fout):
  n_lig=0; n_out=0; n_err=0;
  tags=None;
  url=base_url+('/ligands/%s?smiles=%s'%(search_type, urllib.parse.quote(smi)))
  rval=rest.GetURL(url, parse_json=True)
  ligs=rval
  for lig in ligs:
    n_lig+=1
    if n_lig==1 or not tags:
      tags=sorted(lig.keys())
      fout.write(('\t'.join(tags))+'\n')
    vals=[]
    for tag in tags:
      vals.append((lig[tag]) if tag in lig else '')
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1
    
  logging.info('n_lig: %d'%n_lig)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetSynonyms(base_url, resource, ids, fout):
  '''resource = targets|ligands'''
  n_qry=0; n_syn=0; n_out=0; n_err=0;
  tags=None;
  for id_query in ids:
    n_qry+=1
    url=base_url+'/%s/%s/synonyms'%(resource, id_query)
    rval=rest.GetURL(url, parse_json=True)
    syns=rval
    for syn in syns:
      n_syn+=1
      if n_syn==1 or not tags:
        tags=sorted(syn.keys())
        fout.write(('\t'.join(['%s_id'%resource]+tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((syn[tag]) if tag in syn else '')
      fout.write(('\t'.join([id_query]+vals))+'\n')
      n_out+=1

  logging.info('n_syn: %d'%n_syn)
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetDblinks(base_url, resource, ids, species, db, fout):
  n_qry=0; n_dbl=0; n_out=0; n_err=0;
  tags=None;
  for id_query in ids:
    n_qry+=1
    url=base_url+'/%s/%s/databaseLinks?'%(resource, id_query)
    if species: url+=('&species=%s'%urllib.parse.quote(species))
    if db: url+=('&database=%s'%urllib.parse.quote(db))
    rval=rest.GetURL(url, parse_json=True)
    dbls=rval
    for dbl in dbls:
      n_dbl+=1
      if n_dbl==1 or not tags:
        tags=sorted(dbl.keys())
        fout.write(('\t'.join(['%s_id'%resource]+tags))+'\n')
      vals=[]
      for tag in tags:
        vals.append((dbl[tag]) if tag in dbl else '')
      fout.write(('\t'.join([id_query]+vals))+'\n')
      n_out+=1

  logging.info('n_dbl: %d'%n_dbl)
  logging.info('n_out: %d'%n_out)

#############################################################################
