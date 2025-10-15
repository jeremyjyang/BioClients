#!/usr/bin/env python3
"""
V1:
 - https://www.ebi.ac.uk/gwas/rest/docs/api

V2:
 - https://www.ebi.ac.uk/gwas/rest/api/v2/docs
 - "GWAS RESTful API V2 has been released with various enhancements & improvements over GWAS RESTful API V1. V1 is deprecated and will be retired no later than May 2026."
 - https://www.ebi.ac.uk/gwas/rest/api/v2/docs/reference
"""
###
import sys,os,re,json,time,logging,tqdm
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.request,urllib.parse
import pandas as pd
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/gwas/rest/api'
API_BASE_PATH_V2='/gwas/rest/api/v2'
BASE_URL='https://'+API_HOST+API_BASE_PATH
BASE_URL_V2='https://'+API_HOST+API_BASE_PATH_V2
#
NCHUNK=100;
#
##############################################################################
def InitiateSession():
  retry_strategy = Retry(
	total=10,
	status=4,
	backoff_factor=2,
	status_forcelist=[413, 429, 500, 502, 503, 504],
    allowed_methods=Retry.DEFAULT_ALLOWED_METHODS
	)
  adapter = HTTPAdapter(max_retries=retry_strategy)
  session = requests.Session()
  session.mount("https://", adapter)
  session.mount("http://", adapter)
  return session

##############################################################################
def GetMetadataV2(base_url=BASE_URL_V2, fout=None):
  session = InitiateSession()
  url_this = base_url+f'/metadata'
  response = session.get(url_this)
  if (response.status_code!=200):
    logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
    return
  try:
    rval = response.json()
  except Exception as e:
    logging.error(f"{str(e)}; response.text: {response.text}")
    return
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  metadata = rval['_embedded']['mappingMetadatas'][0]
  for key in metadata.keys():
    metadata[key] = [metadata[key]]
  df_this = pd.DataFrame.from_dict(metadata)
  if fout is not None:
    df_this.to_csv(fout, sep="\t", index=False, header=True)
  return df_this

##############################################################################
def ListStudies(base_url=BASE_URL, fout=None):
  """Only simple metadata."""
  tags=[]; n_study=0; rval=None; df=None; tq=None;
  session = InitiateSession()
  url_this = base_url+f'/studies?size={NCHUNK}'
  while True:
    logging.debug(url_this)
    response = session.get(url_this)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      break
    try:
      rval = response.json()
    except Exception as e:
      logging.error(f"{str(e)}; response.text: {response.text}")
      break
    if '_embedded' not in rval or 'studies' not in rval['_embedded']: break
    studies = rval['_embedded']['studies']
    if studies is None: break
    if tq is None: tq = tqdm.tqdm(total=rval["page"]["totalElements"])
    for study in studies:
      tq.update(n=1)
      if not tags:
        tags = list(study.keys())
        for tag in tags[:]:
          if type(study[tag]) in (list, dict) and tag not in (
                  "diseaseTrait", #V1
                  "disease_trait", #V2
                  "efo_traits", #V2
                  "genotyping_technologies", #V2
                  "discovery_ancestry" #V2
                  ):
            tags.remove(tag)
            logging.info(f"Ignoring tag: {tag}")
      df_this = pd.DataFrame({tag:[str(study[tag]) if tag in study else ''] for tag in tags})
      if fout is not None: df_this.to_csv(fout, sep="\t", index=False, header=(n_study==0), mode=('w' if n_study==0 else 'a'))
      else: df = pd.concat([df, df_this])
      n_study+=1
    if 'next' not in rval['_links']: break
    elif url_this == rval['_links']['last']['href']: break
    else: url_this = rval['_links']['next']['href']
  logging.info(f"n_study: {n_study}")
  return(df)

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
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = url+f'/{id_this}/associations?projection=associationByStudy'
    response = requests.get(url_this)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      continue
    rval = response.json()
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
      df_assn = pd.DataFrame({tag_assn:[assn[tag_assn]] for tag_assn in tags_assn})
      df_study = pd.DataFrame({tag_study:[assn['study'][tag_study]] for tag_study in tags_study})
      df_locus = pd.DataFrame({tag_locus:[assn['loci'][0][tag_locus]] for tag_locus in tags_locus})
      df_locus.columns = ['locus_'+s for s in df_locus.columns]
      df_sra = pd.DataFrame({tag_sra:[assn['loci'][0]['strongestRiskAlleles'][0][tag_sra]] for tag_sra in tags_sra})
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
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=(n_id==0), mode=('w' if n_id==0 else 'a'))
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
def GetStudyAssociationsV2(ids, skip=0, nmax=None, base_url=BASE_URL_V2, fout=None):
  """
https://www.ebi.ac.uk/gwas/rest/api/v2/associations?accession_id=GCST000854&page=0&size=20
sea = SNP effect allele
  """
  n_id=0; n_assn=0; df=None; tq=None;
  tags_assn=[];
  gcsts=set([]); snps=set([]); loci=set([]); seas=set([]); 
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  if skip>0: logging.info(f"SKIP IDs skipped: {skip}")
  for id_this in ids[skip:]:
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = base_url+f'/associations?accession_id={id_this}'
    response = requests.get(url_this)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      continue
    rval = response.json()
    if not rval: continue
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
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
      df_assn = pd.DataFrame({tag_assn:[assn[tag_assn]] for tag_assn in tags_assn})
      if 'accession_id' in assn: gcsts.add(assn['accession_id'])
      links = assn['_links'] if '_links' in assn else {}
      loci_this = links['loci']['href'] if 'loci' in links and 'href' in links['loci'] else {}
      snps_this = links['snp']['href'] if 'snp' in links and 'href' in links['snp'] else {}
      if loci_this:
        loci.add(loci_this)
        df_assn['loci'] = [str(loci_this)]
      else:
        df_assn['loci'] = []
      if snps_this:
        snps.add(snps_this)
        df_assn['snps'] = [str(snps_this)]
      else:
        df_assn['snps'] = []
      seas_this = assn['snp_effect_allele'] if 'snp_effect_allele' in assn else []
      if seas_this:
        df_assn['seas'] = [str(seas_this)]
      else:
        df_assn['seas'] = []
      for sea in seas_this:
        seas.add(sea)
      df_this = pd.concat([df_this, df_assn], axis=0)
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=(n_id==0), mode=('w' if n_id==0 else 'a'))
    if fout is None: df = pd.concat([df, df_this], axis=0)
    n_id+=1
    if n_id==nmax:
      logging.info(f"NMAX IDs reached: {nmax}")
      break
  if tq is not None: tq.close()
  n_gcst = len(gcsts)
  n_loci = len(loci)
  n_snp = len(snps)
  n_sea = len(seas)
  logging.info(f"INPUT RCSTs: {n_id}; OUTPUT RCSTs: {n_gcst} ; assns: {n_assn} ; loci: {n_loci} ; alleles: {n_sea} ; snps: {n_snp}")
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
  session = InitiateSession()
  url = base_url+'/singleNucleotidePolymorphisms'
  if skip>0: logging.info(f"SKIP IDs skipped: {skip}")
  for id_this in ids[skip:]:
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = url+'/'+id_this
    #response = requests.get(url_this)
    try:
      response = session.get(url_this)
    except Exception as e:
      logging.error(f"Failed for SNP:{id_this}; URL:{url_this}; {str(e)}")
      continue
    if response.status_code!=200:
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      continue
    snp = response.json()
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
      df_snp = pd.DataFrame({tag_snp:[snp[tag_snp]] for tag_snp in tags_snp})
      df_gc = pd.DataFrame({tag_gc:[gc[tag_gc]] for tag_gc in tags_gc})
      gcloc = gc['location']
      df_gcloc = pd.DataFrame({tag_gcloc:[gcloc[tag_gcloc]] for tag_gcloc in tags_gcloc})
      gene = gc['gene']
      try: gene["ensemblGeneIds"] = (",".join([gid["ensemblGeneId"] for gid in gene["ensemblGeneIds"]]))
      except: pass
      try: gene["entrezGeneIds"] = (",".join([gid["entrezGeneId"] for gid in gene["entrezGeneIds"]]))
      except: pass
      df_gene = pd.DataFrame({tag_gene:[gene[tag_gene]] for tag_gene in tags_gene})
      df_snp = pd.concat([df_snp, df_gc, df_gcloc, df_gene], axis=1)
      df_this = pd.concat([df_this, df_snp], axis=0)
      n_gene+=1
    if tq is not None: tq.close()
    if fout: df_this.to_csv(fout, sep="\t", index=False, header=(n_snp==0), mode=('w' if n_snp==0 else 'a'))
    if fout is None: df = pd.concat([df, df_this], axis=0)
    n_snp+=1
    if n_snp==nmax:
      logging.info(f"NMAX IDs reached: {nmax}")
      break
  logging.info(f"SNPs: {n_snp}; genes: {n_gene}")
  if fout is None: return(df)

##############################################################################
def GetSnpsV2(ids, skip=0, nmax=None, base_url=BASE_URL_V2, fout=None):
  """
Input: rs_id, e.g. rs7329174
https://www.ebi.ac.uk/gwas/rest/api/v2/single-nucleotide-polymorphisms?rs_id=rs7329174&page=0&size=20
To do(?): Include genomic contexts
  """
  n_snp=0; n_gene=0; n_loc=0; n_gc=0; df=None; tq=None;
  tags_snp=[]; tags_gc=[];
  quiet = bool(logging.getLogger().getEffectiveLevel()>15)
  session = InitiateSession()
  url = base_url+'/single-nucleotide-polymorphisms'
  if skip>0: logging.info(f"SKIP IDs skipped: {skip}")
  for id_this in ids[skip:]:
    if not quiet and tq is None: tq = tqdm.tqdm(total=len(ids)-skip)
    if tq is not None: tq.update()
    url_this = url+f"?rs_id={id_this}"
    try:
      response = session.get(url_this)
    except Exception as e:
      logging.error(f"Failed for SNP:{id_this}; URL:{url_this}; {str(e)}")
      continue
    if response.status_code!=200:
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      continue

    rval = response.json()
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    snps = rval['_embedded']['snps'] if '_embedded' in rval and 'snps' in rval['_embedded'] else []
    df_this=None;
    for snp in snps:
      if not tags_snp:
        for key,val in snp.items():
          if type(val) not in (list, dict): tags_snp.append(key)
      df_snp = pd.DataFrame({tag_snp:[snp[tag_snp]] for tag_snp in tags_snp})
      if 'mapped_genes' in snp:
        df_snp['mapped_genes'] = [','.join(snp['mapped_genes'])]
        n_gene += len(snp['mapped_genes'])
      links = snp['_links'] if '_links' in snp else {}
      gcs_url = links['genomic_contexts']['href'] if 'genomic_contexts' in links and 'href' in links['genomic_contexts'] else None
      df_snp['genomic_contexts_url'] = [gcs_url]

      locs = snp['locations'] if 'locations' in snp else []
      locs_strs = []
      for loc in locs:
        cn = loc['chromosome_name'] if 'chromosome_name' in loc else ''
        cp = loc['chromosome_position'] if 'chromosome_position' in loc else ''
        cr = loc['region']['name'] if 'region' in loc and 'name' in loc['region'] else ''
        locs_strs.append(f"{cn}|{cp}|{cr}")
      df_snp['locations'] = [','.join(locs_strs)]
      n_loc += len(locs)

      rs_id = snp['rs_id'] if 'rs_id' in snp else None
      gcs = GetGenomicContextsV2(rs_id, session)
      df_gc = None
      for gc in gcs:
        if not tags_gc:
          for key,val in gc.items():
            if type(val) not in (list, dict): tags_gc.append(key)
        df_gc = pd.concat([df_gc, pd.DataFrame({tag_gc:[gc[tag_gc]] for tag_gc in tags_gc})])
      n_gc += len(gcs)
      df_snp = pd.concat([df_snp, df_gc], axis=1)
      df_this = pd.concat([df_this, df_snp], axis=0)

    if fout: df_this.to_csv(fout, sep="\t", index=False, header=(n_snp==0), mode=('w' if n_snp==0 else 'a'))
    if fout is None: df = pd.concat([df, df_this], axis=0)
    n_snp+=1
    if n_snp==nmax:
      logging.info(f"NMAX IDs reached: {nmax}")
      break
  if tq is not None: tq.close()
  logging.info(f"SNPs: {n_snp}; mapped_genes: {n_gene}; locations: {n_loc}; genomic_contexts: {n_gc}")
  if fout is None: return(df)

##############################################################################
def GetGenomicContextsV2(rs_id, session):
  """
https://www.ebi.ac.uk/gwas/rest/api/v2/single-nucleotide-polymorphisms/rs7329174/genomic-contexts?sort=distance&direction=asc
  """
  if not rs_id: return []
  url_this = f"https://www.ebi.ac.uk/gwas/rest/api/v2/single-nucleotide-polymorphisms/{rs_id}/genomic-contexts?sort=distance&direction=asc"
  try:
    response = session.get(url_this)
  except Exception as e:
    logging.error(f"Failed for SNP:{rs_id}; URL:{url_this}; {str(e)}")
    return []
  if response.status_code!=200:
    logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
    return []
  rval = response.json()
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  gcs = rval['_embedded']['genomic_contexts'] if '_embedded' in rval and 'genomic_contexts' in rval['_embedded'] else []
  return gcs

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
    response = requests.get(url_this)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code}): url_this: {url_this}")
      break
    rval = response.json()
    if not rval or '_embedded' not in rval or 'studies' not in rval['_embedded']: continue
    studies = rval['_embedded']['studies']
    if not studies: continue
    for study in studies:
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict) or tag=="diseaseTrait":
            tags.append(tag) #Only simple metadata.
      n_study+=1
      df_this = pd.DataFrame({tag:[str(study[tag]) if tag in study else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  logging.info(f"n_study: {n_study}")
  if fout is None: return(df)

##############################################################################
