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
  tags=[]; n_study=0; rval=None; df=None; tq=None;
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
    if tq is None: tq = tqdm.tqdm(total=rval["page"]["totalElements"], unit="studies")
    for study in studies:
      tq.update()
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict) or tag=="diseaseTrait":
            tags.append(tag) #Only simple metadata.
      df_this = pd.DataFrame({tags[j]:([str(study[tags[j]])] if tags[j] in study else ['']) for j in range(len(tags))})
      if fout: df_this.to_csv(fout, "\t", index=False, header=(n_study==0), mode=('w' if n_study==0 else 'a'))
      if fout is None: df = pd.concat([df, df_this])
      n_study+=1
  logging.info(f"n_study: {n_study}")
  if fout is None: return(df)

##############################################################################
def GetStudyAssociations(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """
Mapped genes via SNP links.
arg = authorReportedGene
sra = strongestRiskAllele
https://www.ebi.ac.uk/gwas/rest/api/studies/GCST001430/associations?projection=associationByStudy
  """
  n_id=0; n_assn=0; n_loci=0; n_arg=0; n_sra=0; n_snp=0; df=None; tq=None;
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  gcsts=set([]); tags_assn=[]; tags_study=[]; tags_locus=[]; tags_sra=[]; tags_arg=[];
  url = base_url+'/studies'
  if skip>0: logging.info(f"SKIP IDs skipped: {skip}")
  for id_this in ids[skip:]:
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip, unit="studies")
    if tq is not None: tq.update()
    url_this = url+f'/{id_this}/associations?projection=associationByStudy'
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    if not rval: continue
    if '_embedded' in rval and 'associations' in rval['_embedded']:
      assns = rval['_embedded']['associations']
    else:
      logging.error(f'No associations for study: {id_this}')
      continue
    df_this=None;
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
      df_assn = pd.concat([df_assn, df_study, df_locus, df_sra], axis=1)
      df_this = pd.concat([df_this, df_assn], axis=0)
      if 'accessionId' in assn['study']: gcsts.add(assn['study']['accessionId'])
      n_loci += len(assn['loci'])
      for locus in assn['loci']:
        n_sra += len(locus['strongestRiskAlleles'])
        for sra in locus['strongestRiskAlleles']:
          snp_href = sra['_links']['snp']['href'] if '_links' in sra and 'snp' in sra['_links'] and 'href' in sra['_links']['snp'] else ''
          if snp_href: n_snp+=1
    if fout: df_this.to_csv(fout, "\t", index=False, header=(n_id==0), mode=('w' if n_id==0 else 'a'))
    if fout is None: df = pd.concat([df, df_this], axis=0)
    n_id+=1
    if n_id==nmax:
      logging.info(f"NMAX IDs reached: {nmax}")
      break
  if tq is not None: tq.close()
  n_gcst = len(gcsts)
  logging.info(f"INPUT RCSTs: {n_id}; OUTPUT RCSTs: {n_gcst} ; assns: {n_assn} ; loci: {n_loci} ; alleles: {n_sra} ; snps: {n_snp}")
  if fout is None: return(df)

##############################################################################
def GetSnps(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """
Input: rs_id, e.g. rs7329174
loc = location
gc = genomicContext
  """
  n_snp=0; n_gene=0; n_loc=0; df=None; tq=None;
  tags_snp=[]; tags_loc=[]; tags_gc=[]; tags_gcloc=[];  tags_gene=[]; 
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  url = base_url+'/singleNucleotidePolymorphisms'
  if skip>0: logging.info(f"SKIP IDs skipped: {skip}")
  for id_this in ids[skip:]:
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip, unit="snps")
    if tq is not None: tq.update()
    url_this = url+'/'+id_this
    snp = rest.Utils.GetURL(url_this, parse_json=True)
    if not snp: continue
    if 'genomicContexts' not in snp: continue
    if len(snp['genomicContexts'])==0: continue
    df_this=None;
    for gc in snp['genomicContexts']:
      if not tags_snp:
        for key,val in snp.items():
          if type(val) not in (list, dict): tags_snp.append(key)
        for key in gc.keys():
          if key not in ('gene', 'location', '_links'): tags_gc.append(key)
        for key in gc['location'].keys():
          if key != '_links': tags_gcloc.append(key)
        for key in gc['gene'].keys():
          if key != '_links': tags_gene.append(key)
      df_snp = pd.DataFrame({tags_snp[j]:[snp[tags_snp[j]]] for j in range(len(tags_snp))})
      df_gc = pd.DataFrame({tags_gc[j]:[gc[tags_gc[j]]] for j in range(len(tags_gc))})
      gcloc = gc['location']
      df_gcloc = pd.DataFrame({tags_gcloc[j]:[gcloc[tags_gcloc[j]]] for j in range(len(tags_gcloc))})
      gene = gc['gene']
      try: gene["ensemblGeneIds"] = (",".join([gid["ensemblGeneId"] for gid in gene["ensemblGeneIds"]]))
      except: pass
      try: gene["entrezGeneIds"] = (",".join([gid["entrezGeneId"] for gid in gene["entrezGeneIds"]]))
      except: pass
      df_gene = pd.DataFrame({tags_gene[j]:[gene[tags_gene[j]]] for j in range(len(tags_gene))})
      df_snp = pd.concat([df_snp, df_gc, df_gcloc, df_gene], axis=1)
      df_this = pd.concat([df_this, df_snp], axis=0)
      n_gene+=1
    if tq is not None: tq.close()
    if fout: df_this.to_csv(fout, "\t", index=False, header=(n_snp==0), mode=('w' if n_snp==0 else 'a'))
    if fout is None: df = pd.concat([df, df_this], axis=0)
    n_snp+=1
    if n_snp==nmax:
      logging.info(f"NMAX IDs reached: {nmax}")
      break
  logging.info(f"SNPs: {n_snp}; genes: {n_gene}")
  if fout is None: return(df)

##############################################################################
def SearchStudies(ids, searchtype, base_url=BASE_URL, fout=None):
  tags=[]; n_study=0; rval=None; df=None; tq=None;
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
      df_this = pd.DataFrame({tags[j]:([str(study[tags[j]])] if tags[j] in study else ['']) for j in range(len(tags))})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  logging.info(f"n_study: {n_study}")
  if fout is None: return(df)

##############################################################################
