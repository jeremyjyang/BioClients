#!/usr/bin/env python3
'''

https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/

Parse, process Entrez PubMed XML (summaries or full), normally obtained via Entrez eUtils,
e.g. entrez_pubmed_search.pl.

Note that other Entrez XML (e.g. PubChem) very similar.
'''
import os,sys,re,time,argparse,logging

from xml.etree import ElementTree
from xml.parsers import expat

from .. import util

#############################################################################
def PubMed_Docsum2Tsv(tree, fout):
  '''From summary xml, extract 1st occurance of selected fields.'''
  docsums = util.xml.XpathFind('/eSummaryResult/DocSum', tree)
  tags = ['PubDate', 'EPubDate', 'Source', 'Title', 'ISSN', 'PubTypeList', 'FullJournalName',
	'LastAuthor', 'SO', 'DOI', 'ELocationID',
	'pmc'] ##pmc is special
  fout.write(('\t'.join(['Id']+tags))+'\n')
  for docsum in docsums:
    pubdata = {}
    for cnode in docsum.childNodes:
      if cnode.nodeName == 'Id':
        pubdata['Id'] = util.xml.DOM_NodeText(cnode)
      for tag in tags:
        if cnode.nodeName == 'Item' and util.xml.DOM_GetNodeAttr(cnode, 'Name')==tag:
          pubdata[tag] = util.xml.DOM_NodeText(cnode)
        if cnode.nodeName == 'Item' and util.xml.DOM_GetNodeAttr(cnode, 'Name')=="ArticleIds":
          for cnode2 in cnode.childNodes:
            if cnode2.nodeName == 'Item' and util.xml.DOM_GetNodeAttr(cnode2, 'Name')=="pmc":
              pubdata['pmc'] = util.xml.DOM_NodeText(cnode2)
    for j,tag in enumerate(['Id']+tags):
      fout.write('\t' if j>0 else '')
      fout.write('"%s"'%(pubdata[tag] if pubdata.has_key(tag) else ''))
    fout.write('\n')
  logging.info('DocSum count: %d'%len(docsums))
  return

#############################################################################
def PubMed_Doc2Tsv(tree, fout):
  '''From full xml, extract 1st occurance of selected fields.'''
  citations = util.xml.XpathFind('/PubmedArticleSet/PubmedArticle/MedlineCitation', tree)
  xps = [	#relative xpaths
	'PMID',
	'Article/Journal/JournalIssue/PubDate/Year',
	'Article/Journal/Title',
	'Article/Journal/ISSN',
	'Article/PublicationTypeList/PublicationType',
	'Article/ArticleTitle',
	#'Article/Abstract/AbstractText',
	'Article/AuthorList/Author/LastName'
	]
  fout.write(('\t'.join(map(lambda p:os.path.basename(p), xps)))+'\n')
  for citation in citations:
    for j,xp in enumerate(xps):
      nodes = util.xml.XpathFind(xp, citation)
      datum = util.xml.DOM_NodeText(nodes[0]) if nodes else ''
      fout.write('\t' if j>0 else '')
      fout.write('"%s"'%(datum))
    fout.write('\n')
  logging.info('citation count: %d'%len(citations))
  return

#############################################################################
def PubMed_Doc2AuthorList(tree, fout):
  '''From full xml for one pub, extract author list.'''
  authors = util.xml.XpathFind('/PubmedArticleSet/PubmedArticle/MedlineCitation/Article/AuthorList/Author', tree)
  for author in authors:
    n = util.xml.XpathFind('LastName', author)
    lname = util.xml.DOM_NodeText(n[0])
    fname = util.xml.DOM_NodeText(util.xml.XpathFind('ForeName', author)[0])
    affiliations = util.xml.XpathFind('AffiliationInfo/Affiliation', author)
    affs=[]
    for affiliation in affiliations:
      affs.append(util.xml.DOM_NodeText(affiliation))
    fout.write('"%s"\t"%s"\t"%s"\n'%(lname, fname, ('; '.join(affs))))
  logging.info('n_authors: %d'%len(authors))

#############################################################################
def PubMed_Docsum2AbstractText(tree, pmid, fout, verbose):
  '''From summary xml, extract title and abstract.'''
  articles = util.xml.XpathFind('/PubmedArticleSet/PubmedArticle', tree)
  title=None; abstract=None;
  for article in articles:
    try:
      pmid_this = int(util.xml.DOM_GetLeafValsByTagName(article, 'PMID')[0])
    except Exception as e:
      logging.error('PMID not found: %s'%str(e))
      continue
    if pmid_this==int(pmid):
      try:
        title = util.xml.DOM_GetLeafValsByTagName(article, 'ArticleTitle')[0]
      except Exception as e:
        logging.info('ERROR: ArticleTitle not found: %s'%str(e))
      try:
        abstract = util.xml.DOM_GetLeafValsByTagName(article, 'AbstractText')[0]
      except Exception as e:
        logging.info('ERROR: AbstractText not found: %s'%str(e))
      break
  if title or abstract:
    if not title: logging.info('ERROR: no title found for PMID: %d'%(pmid))
    if not abstract: logging.info('ERROR: no abstract found for PMID: %d ; title: "%s"'%(pmid, title))
    fout.write('%s\n%s\n'%(title, abstract))
    return True
  else:
    return False

#############################################################################
def PubMed_Doc2AbstractText(tree, pmid, fout, verbose):
  '''From full xml, extract title and abstract.'''
  citations = util.xml.XpathFind('/PubmedArticleSet/PubmedArticle/MedlineCitation', tree)
  title=None; abstract=None;
  for citation in citations:
    try:
      pmid_this = int(util.xml.DOM_GetLeafValsByTagName(citation, 'PMID')[0])
    except Exception as e:
      logging.info('ERROR: PMID not found: %s'%str(e))
      continue
    if pmid_this==int(pmid):
      try:
        title = util.xml.DOM_GetLeafValsByTagName(citation, 'ArticleTitle')[0]
      except Exception as e:
        logging.info('ERROR: ArticleTitle not found: %s'%str(e))
      try:
        abstract = util.xml.DOM_GetLeafValsByTagName(citation, 'AbstractText')[0]
      except Exception as e:
        logging.info('ERROR: AbstractText not found: %s'%str(e))
      break
  if title or abstract:
    if not title: logging.info('ERROR: no title found for PMID: %d'%(pmid))
    if not abstract: logging.info('ERROR: no abstract found for PMID: %d ; title: "%s"'%(pmid, title))
    fout.write('%s\n%s\n'%(title, abstract))
    return True
  else:
    return False

#############################################################################
