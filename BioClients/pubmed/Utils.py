#!/usr/bin/env python3
'''
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
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='process PubMed XML (summaries or full), typically obtained via Entrez eUtils.')
  ops=['summary2tsv', 'summary2abstract', 'full2tsv', 'full2abstract', 'full2authorlist']
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", required=True, help="input file, XML")
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--idfile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="max to return")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--odir", help="output directory")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile)

  pmids=[]
  if args.idfile:
    fin_ids = open(args.idfile)
    if not fin_ids: parser.error('cannot open idfile: %s'%args.idfile)
    while True:
      line = fin_ids.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        logging.error('bad input ID: %s'%line)
        continue
    if args.verbose:
      logging.info('input IDs: %d'%(len(ids)))
    fin_ids.close()

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  try:
    tree = ElementTree.parse(fin)
  except Exception as e:
    parser.error('failed to parse XML: %s'%str(e))

  if args.op == 'summary2tsv':
    PubMed_Docsum2Tsv(tree, fout)

  elif args.op == 'full2tsv':
    PubMed_Doc2Tsv(tree, fout)

  elif args.op == 'full2authorlist':
    PubMed_Doc2AuthorList(tree, fout)

  elif args.op == 'summary2abstract':
    if not ids: parser.error('--summary2abstract requires --ids.')
    n_out=0;
    for id_this in ids:
      logging.info('%08d'%(id_this))
      if args.odir: fout = open('%s/%08d_title_and_abstract.txt'%(args.odir, id_this), "w")
      ok = PubMed_Docsum2AbstractText(tree, id_this, fout, args.verbose)
      if ok: n_out+=1
      else: logging.error('no title or abstract found for PMID: %d'%(id_this))
      if odir: fout.close()
    logging.info('abstracts found: %d'%n_out)

  elif args.op == 'full2abstract':
    if not ids: parser.error('--full2abstract requires --ids.')
    n_out=0;
    for id_this in ids:
      if args.verbose:
        logging.info('%08d'%(id_this))
      if args.odir: fout = open('%s/%08d_title_and_abstract.txt'%(odir, id_this), "w")
      ok = PubMed_Doc2AbstractText(tree, id_this, fout, args.verbose)
      if ok: n_out+=1
      else: logging.error('no title or abstract found for PMID: %d'%(id_this))
      if args.odir: fout.close()
    logging.info('abstracts found: %d'%n_out)

  else:
    parser.error('no operation specified.')
