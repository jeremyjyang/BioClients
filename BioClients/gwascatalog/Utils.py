#!/usr/bin/env python3
"""
https://www.ebi.ac.uk/gwas/rest/docs/api
"""
###
import sys,os,re,json,time,logging,tqdm
import urllib.parse
import pandas as pd
#
from ..util import rest
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/gwas/rest/api'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100;
#
##############################################################################
def ListStudies(base_url=BASE_URL, fout=None):
  """Only simple metadata."""
  tags=[]; n_study=0; rval=None;
  df=pd.DataFrame(); tq=None;
  url_this = base_url+f'/studies?size={NCHUNK}'
  while True:
    if rval:
      if 'next' not in rval['_links']: break
      elif url_this == rval['_links']['last']['href']: break
      else: url_this = rval['_links']['next']['href']
    logging.debug(url_this)
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    if not rval or '_embedded' not in rval or 'studies' not in rval['_embedded']: break
    studies = rval['_embedded']['studies']
    if not studies: break
    if not tq: tq = tqdm.tqdm(total=rval["page"]["totalElements"], unit="studies")
    for study in studies:
      tq.update()
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict) or tag=="diseaseTrait":
            tags.append(tag) #Only simple metadata.
      df = pd.concat([df, pd.DataFrame({tags[j]:[study[tags[j]]] for j in range(len(tags))})])
      n_study+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_study: {n_study}")
  return(df)

##############################################################################
def SearchStudies(ids, searchtype, base_url=BASE_URL, fout=None):
  tags=[]; n_study=0; rval=None;
  df=pd.DataFrame(); tq=None;
  url = base_url+'/studies/search'
  if searchtype=='gcst':
    url+='/'
  elif searchtype.lower()=='pubmedid':
    url+='/findByPublicationIdPubmedId?pubmedId={}'
  elif searchtype.lower()=='efotrait':
    url+='/findByEfoTrait?efoTrait={}'
  elif searchtype.lower()=='efouri':
    url+='/findByEfoUri?efoUri={}'
  elif searchtype.lower()=='accessionid':
    url+='/findByAccessionId?accessionId={}'
  else:
    logging.error(f'Searchtype not supported: {searchtype}')
    return
  for id_this in ids:
    url_this = url.format(urllib.parse.quote(id_this))
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    if not rval or '_embedded' not in rval or 'studies' not in rval['_embedded']: continue
    studies = rval['_embedded']['studies']
    if not studies: continue
    for study in studies:
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict) or tag=="diseaseTrait":
            tags.append(tag) #Only simple metadata.
      n_study+=1
      df = pd.concat([df, pd.DataFrame({tags[j]:[study[tags[j]]] for j in range(len(tags))})])
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_study: {n_study}")
  return(df)

##############################################################################
def GetStudyAssociations(ids, base_url=BASE_URL, fout=None):
  """
Mapped genes via SNP links.
arg = authorReportedGene
sra = strongestRiskAllele
https://www.ebi.ac.uk/gwas/rest/api/studies/GCST001430/associations?projection=associationByStudy
  """
  n_id=0; n_assn=0; n_loci=0; n_arg=0; n_sra=0; n_snp=0; gcsts=set([])
  tags_assn=[]; tags_study=[]; tags_locus=[]; tags_sra=[]; tags_arg=[];
  df=pd.DataFrame(); tq=None;
  url = base_url+'/studies'
  for id_this in ids:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="studies")
    tq.update()
    n_id+=1
    url_this = url+f'/{id_this}/associations?projection=associationByStudy'
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    if not rval: continue
    if '_embedded' in rval and 'associations' in rval['_embedded']:
      assns = rval['_embedded']['associations']
    else:
      logging.error(f'No associations for study: {id_this}')
      continue
    for assn in assns:
      n_assn+=1
      if n_assn==1:
        for key,val in assn.items():
          if type(val) not in (list, dict):
            tags_assn.append(key)
        for key in assn['study'].keys():
          if type(assn['study'][key]) not in (list, dict):
            tags_study.append(key)
        for key in assn['loci'][0].keys():
          if key not in ('strongestRiskAlleles', 'authorReportedGenes'):
            tags_locus.append(key)
        for key in assn['loci'][0]['strongestRiskAlleles'][0].keys():
          if key != '_links':
            tags_sra.append(key)
      df_assn = pd.DataFrame({tags_assn[j]:[assn[tags_assn[j]]] for j in range(len(tags_assn))})
      df_study = pd.DataFrame({tags_study[j]:[assn['study'][tags_study[j]]] for j in range(len(tags_study))})
      df_locus = pd.DataFrame({tags_locus[j]:[assn['loci'][0][tags_locus[j]]] for j in range(len(tags_locus))})
      df_locus.columns = ['locus_'+s for s in df_locus.columns]
      df_sra = pd.DataFrame({tags_sra[j]:[assn['loci'][0]['strongestRiskAlleles'][0][tags_sra[j]]] for j in range(len(tags_sra))})
      df_sra.columns = ['allele_'+s for s in df_sra.columns]
      df_this = pd.concat([df_assn,df_study, df_locus, df_sra], axis=1)
      df = pd.concat([df, df_this], axis=0)
      if 'accessionId' in assn['study']: gcsts.add(assn['study']['accessionId'])
      n_loci += len(assn['loci'])
      for locus in assn['loci']:
        n_sra += len(locus['strongestRiskAlleles'])
        for sra in locus['strongestRiskAlleles']:
          snp_href = sra['_links']['snp']['href'] if '_links' in sra and 'snp' in sra['_links'] and 'href' in sra['_links']['snp'] else ''
          if snp_href: n_snp+=1
  n_gcst = len(gcsts)
  logging.info(f"INPUT RCSTs: {n_id}; OUTPUT RCSTs: {n_gcst} ; assns: {n_assn} ; loci: {n_loci} ; alleles: {n_sra} ; snps: {n_snp}")
  if fout: df.to_csv(fout, "\t", index=False)
  return(df)

##############################################################################
def GetSnps(ids, base_url=BASE_URL, fout=None):
  """
Input: rs_id, e.g. rs7329174
loc = location
gc = genomicContext
  """
  n_snp=0; n_gc=0; n_gene=0; n_gcloc=0; n_loc=0;
  tags_snp=[]; tags_loc=[]; tags_gc=[]; tags_gcloc=[];  tags_gene=[]; 
  df=pd.DataFrame(); tq=None;
  url = base_url+'/singleNucleotidePolymorphisms'
  for id_this in ids:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="snps")
    tq.update()
    n_snp+=1
    url_this = url+'/'+id_this
    snp = rest.Utils.GetURL(url_this, parse_json=True)
    if not snp: continue
    if n_snp==1:
      for key,val in snp.items():
        if type(val) not in (list, dict):
          tags_snp.append(key)
      for key in snp['genomicContexts'][0].keys():
        if key not in ('gene', 'location', '_links'):
          tags_gc.append(key)
      for key in snp['genomicContexts'][0]['location'].keys():
        if key != '_links':
          tags_gcloc.append(key)
      for key in snp['genomicContexts'][0]['gene'].keys():
        if key != '_links':
          tags_gene.append(key)
      df_snp = pd.DataFrame({tags_snp[j]:[snp[tags_snp[j]]] for j in range(len(tags_snp))})
      df_gc = pd.DataFrame({tags_gc[j]:[snp['genomicContexts'][0][tags_gc[j]]] for j in range(len(tags_gc))})
      df_gcloc = pd.DataFrame({tags_gcloc[j]:[snp['genomicContexts'][0]['location'][tags_gcloc[j]]] for j in range(len(tags_gcloc))})
      df_gene = pd.DataFrame({tags_gene[j]:[snp['genomicContexts'][0]['gene'][tags_gene[j]]] for j in range(len(tags_gene))})
      df_this = pd.concat([df_snp, df_gc, df_gcloc, df_gene], axis=1)
      df = pd.concat([df, df_this], axis=0)
    for gc in snp['genomicContexts']:
      n_gc+=1
      gcloc = gc['location']
      n_gcloc+=1
      gene = gc['gene']
      n_gene+=1
  logging.info(f"SNPs: {n_snp}; genomicContexts: {n_gc}; genes: {n_gene}; locations: {n_gcloc}")
  if fout: df.to_csv(fout, "\t", index=False)
  return(df)

##############################################################################
