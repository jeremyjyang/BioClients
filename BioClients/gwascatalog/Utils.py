#!/usr/bin/env python3
###
import sys,os,re,json,time,logging
#
from ..util import rest_utils
#
##############################################################################
def ListStudies(base_url, fout):
  """Only simple metadata."""
  url_this=base_url+'/studies?size=100'
  tags=[]; n_study=0; rval=None;
  while True:
    if rval:
      if 'next' not in rval['_links']: break
      elif url_this == rval['_links']['last']['href']: break
      else: url_this = rval['_links']['next']['href']
    logging.debug(url_this)
    rval = rest_utils.GetURL(url_this, parse_json=True)
    if not rval or '_embedded' not in rval or 'studies' not in rval['_embedded']: break
    studies = rval['_embedded']['studies']
    if not studies: break
    for study in studies:
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
        fout.write('\t'.join(tags)+'\n')
      n_study+=1
      vals = [str(study[tag]).replace('\n', ' ') if tag in study and study[tag] is not None else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
  logging.info('n_study: {0}'.format(n_study))

##############################################################################
def SearchStudies(base_url, ids, searchtype, fout):
  url=base_url+'/studies/search'
  if searchtype=='gcst':
    url+='/'
  elif searchtype.lower()=='pubmedid':
    url+='/findByPublicationIdPubmedId?pubmedId='
  elif searchtype.lower()=='efotrait':
    url+='/findByEfoTrait?efoTrait='
  elif searchtype.lower()=='efouri':
    url+='/findByEfoUri?efoUri='
  elif searchtype.lower()=='accessionid':
    url+='/findByAccessionId?accessionId='
  else:
    logging.error('Not yet supported: searchtype: %s'%(searchtype))
    return
  tags=[]; n_study=0; rval=None;
  for id_this in ids:
    url_this=url+'%s'%id_this
    rval = rest_utils.GetURL(url_this, parse_json=True)
    if not rval or '_embedded' not in rval or 'studies' not in rval['_embedded']: continue
    studies = rval['_embedded']['studies']
    if not studies: continue
    for study in studies:
      if not tags:
        for tag in study.keys():
          if type(study[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
        fout.write('\t'.join(tags)+'\n')
      n_study+=1
      vals = [str(study[tag]).replace('\n', ' ') if tag in study and study[tag] is not None else '' for tag in tags]
      fout.write('\t'.join(vals)+'\n')
    logging.debug('%s'%json.dumps(rval, sort_keys=True, indent=2))
  logging.info('n_study: {0}'.format(n_study))

##############################################################################
def GetStudyAssociations(base_url, ids, fout):
  """
	Mapped genes via SNP links.
	arg = authorReportedGene
	sra = strongestRiskAllele
	https://www.ebi.ac.uk/gwas/rest/api/studies/GCST002264/associations?projection=associationByStudy
  """
  url=base_url+'/studies'
  n_id=0; n_assn=0; n_loci=0; n_arg=0; n_sra=0; n_snp=0; gcsts=set([])
  tags_assn=[]; tags_study=[]; tags_locus=[]; tags_sra=[]; tags_arg=[];
  for id_this in ids:
    n_id+=1
    url_this=url+'/%s/associations?projection=associationByStudy'%id_this
    rval=rest_utils.GetURL(url_this, parse_json=True)
    if not rval:
      continue
    if '_embedded' in rval and 'associations' in rval['_embedded']:
      assns = rval['_embedded']['associations']
    else:
      logging.error('ERROR: no associations for study: %s'%id_this)
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
#        for key in assn['loci'][0]['authorReportedGenes'][0].keys():
#          tags_arg.append(key)
        fout.write('\t'.join(list(map(lambda s: 'study_'+s, tags_study))
		+tags_assn
		+list(map(lambda s: 'locus_'+s, tags_locus))
#		+list(map(lambda s: 'reported_'+s, tags_arg))
		+list(map(lambda s: 'allele_'+s, tags_sra))
		+['snp_url'])+'\n')

      vals=[];
      for tag in tags_study:
        vals.append(CleanStr(assn['study'][tag]) if tag in assn['study'] and assn['study'][tag] is not None else '')
        try: gcsts.add(assn['study']['accessionId'])
        except: pass
      for tag in tags_assn:
        vals.append(CleanStr(assn[tag]) if tag in assn and assn[tag] is not None else '')
      for locus in assn['loci']:
        n_loci+=1
        vals_locus=[];
        for tag in tags_locus:
          vals_locus.append(CleanStr(locus[tag]) if tag in locus and locus[tag] is not None else '')

      ## Ignore reported genes.
#        for arg in locus['authorReportedGenes']:
#          n_arg+=1
#          vals_arg=[];
#          for tag in tags_arg:
#            if tag=='entrezGeneIds':
#              geneids = [g['entrezGeneId'] for g in arg[tag]]
#              if None in geneids: geneids.remove(None)
#              vals_arg.append(';'.join(geneids) if geneids else '')
#            elif tag=='ensemblGeneIds':
#              geneids = [g['ensemblGeneId'] for g in arg[tag]]
#              if None in geneids: geneids.remove(None)
#              vals_arg.append(';'.join(geneids) if geneids else '')
#            else:
#              vals_arg.append(CleanStr(arg[tag]) if tag in arg else '')
#          fout.write('\t'.join(vals+vals_locus+vals_arg+['' for tag in tags_sra]+[''])+'\n')

        for sra in locus['strongestRiskAlleles']:
          n_sra+=1
          vals_sra=[]; snp_href='';
          snp_href = sra['_links']['snp']['href'] if '_links' in sra and 'snp' in sra['_links'] and 'href' in sra['_links']['snp'] else ''
          if snp_href: n_snp+=1
          for tag in tags_sra:
            vals_sra.append(CleanStr(sra[tag]) if tag in sra and sra[tag] is not None else '')
#          fout.write('\t'.join(vals+vals_locus+['' for tag in tags_arg]+vals_sra+[snp_href])+'\n')
          fout.write('\t'.join(vals+vals_locus+vals_sra+[snp_href])+'\n')

#  logging.info('INPUT RCSTs: %d; OUTPUT RCSTs: %d ; assns: %d ; loci: %d ; reportedGenes: %d ; alleles: %d ; snps: %d'%(n_id, len(gcsts), n_assn, n_loci, n_arg, n_sra, n_snp))
  logging.info('INPUT RCSTs: %d; OUTPUT RCSTs: %d ; assns: %d ; loci: %d ; alleles: %d ; snps: %d'%(n_id, len(gcsts), n_assn, n_loci, n_sra, n_snp))

##############################################################################
def GetSnps(base_url, ids, fout):
  """
	loc = location
	gc = genomicContext
  """
  url=base_url+'/singleNucleotidePolymorphisms'
  n_snp=0; n_gc=0; n_gene=0; n_gcloc=0; n_loc=0;
  tags=[]; tags_loc=[]; tags_gc=[]; tags_gcloc=[];  tags_gene=[]; 
  for id_this in ids:
    n_snp+=1
    url_this=url+'/'+id_this
    snp=rest_utils.GetURL(url_this, parse_json=True)
    if not snp:
      continue
    if n_snp==1:
      for key,val in snp.items():
        if type(val) not in (list, dict):
          tags.append(key)
      #for key in snp['locations'][0].keys():
      #  if key != '_links':
      #    tags_loc.append(key)
      for key in snp['genomicContexts'][0].keys():
        if key not in ('gene', 'location', '_links'):
          tags_gc.append(key)
      for key in snp['genomicContexts'][0]['location'].keys():
        if key != '_links':
          tags_gcloc.append(key)
      for key in snp['genomicContexts'][0]['gene'].keys():
        if key != '_links':
          tags_gene.append(key)
      fout.write('\t'.join(tags
		+list(map(lambda s: 'genomicContext_'+s, tags_gc))
		+list(map(lambda s: 'loc_'+s, tags_gcloc))
		+list(map(lambda s: 'gene_'+s, tags_gene)))
		+'\n')
    vals=[];
    for tag in tags:
      vals.append(CleanStr(snp[tag]) if tag in snp and snp[tag] is not None else '')
    for gc in snp['genomicContexts']:
      n_gc+=1
      vals_gc=[];
      for tag in tags_gc:
        vals_gc.append(CleanStr(gc[tag]) if tag in gc and gc[tag] is not None else '')
      gcloc = gc['location']
      n_gcloc+=1
      vals_gcloc=[];
      for tag in tags_gcloc:
        if tag=='region':
          vals_gcloc.append(gcloc[tag]['name'] if tag in gcloc and gcloc[tag] and 'name' in gcloc[tag] and gcloc[tag]['name'] is not None else '')
        else:
          vals_gcloc.append(CleanStr(gcloc[tag]) if tag in gcloc and gcloc[tag] is not None else '')
      gene = gc['gene']
      n_gene+=1
      vals_gene=[];
      for tag in tags_gene:
        if tag=='entrezGeneIds':
          geneids = [g['entrezGeneId'] for g in gene[tag]]
          if None in geneids: geneids.remove(None)
          vals_gene.append(';'.join(geneids) if geneids else '')
        elif tag=='ensemblGeneIds':
          geneids = [g['ensemblGeneId'] for g in gene[tag]]
          if None in geneids: geneids.remove(None)
          vals_gene.append(';'.join(geneids) if geneids else '')
        else:
          vals_gene.append(str(gene[tag]) if tag in gene and gene[tag] is not None else '')
      fout.write('\t'.join(vals+vals_gc+vals_gcloc+vals_gene)+'\n')

  logging.info('SNPs: %d ; genomicContexts: %d ; genes: %d ; locations: %d'%(n_snp, n_gc, n_gene, n_gcloc))

##############################################################################
def CleanStr(val):
  val = re.sub(r'[\t\r\n]', ' ', str(val))
  return val.strip()

