#!/usr/bin/env python3
'''
https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/
'''
import os,sys,io,re,json,time,requests,urllib.parse,logging,tqdm,tqdm.auto
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd

from xml.etree import ElementTree

from .. import util
from ..util import xml as util_xml

API_HOST="eutils.ncbi.nlm.nih.gov"
API_BASE_PATH="/entrez/eutils"
BASE_URL=f"https://{API_HOST}{API_BASE_PATH}"

#############################################################################
def GetESummary(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; n_err=0; tq=None; tags=None; df=None; i_this=0;
  if skip: logging.debug(f"skip: [1-{skip}]")
  for id_this in ids:
    i_this+=1
    if i_this<skip: continue
    if tq is None: tq = tqdm.tqdm(total=(len(ids)-skip if nmax is None else nmax))
    url_this = f"{base_url}/esummary.fcgi?db=pubmed&id={id_this}&retmode=json"
    try:
      response = requests.get(url_this)
    except Exception as e:
      logging.error(f"{e}")
      n_err+=1
      continue
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      continue
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    pubs = result["result"] if "result" in result else []
    uids = pubs["uids"] if "uids" in pubs else []
    for uid in uids:
      pub = pubs[uid] if uid in pubs else None
      if not pub:
        logging.error(f"{i_this}. PMID not found: {id_this}")
        continue #Error
      if tags is None:
        tags = [tag for tag in pub.keys() if type(pub[tag]) not in (list, dict)]
      df_this = pd.DataFrame({tag:[pub[tag]] for tag in tags})
      if fout is not None:
        df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      else:
        df = pd.concat([df, df_this])
    n_out+=1
    tq.update(n=1)
    if nmax is not None and i_this-skip>nmax: break
  tq.close()
  logging.info(f"n_out: {n_out}; n_err: {n_err}")
  return df

#############################################################################
def GetRecord(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """Only get title, abstract, journal, year.  Must process XML since no retmode=json supported."""
  n_out=0; n_err=0; tq=None; tags=None; df=None; i_this=0;
  if skip: logging.debug(f"skip: [1-{skip}]")
  for id_this in ids:
    i_this+=1
    if i_this<skip: continue
    if tq is None: tq = tqdm.tqdm(total=min(len(ids)-skip, nmax if nmax is not None else float("inf")))
    url_this = f"{base_url}/efetch.fcgi?db=pubmed&id={id_this}"
    try:
      response = requests.get(url_this)
    except Exception as e:
      logging.error(f"{e}")
      n_err+=1
      continue
    if response.status_code!=200:
      logging.debug(f"Status code: {response.status_code}")
      continue
    pubxml = response.content.decode('utf-8')
    logging.debug(pubxml)
    try:
      elt = ElementTree.parse(io.StringIO(pubxml))
    except Exception as e:
      logging.error(f"XML parse error: {e}; xml={pubxml}")
      n_err+=1
      continue
    logging.debug(f"XML parsed ok.")
    articles = elt.iterfind("PubmedArticle")
    for article in articles:
      logging.debug(f"article.tag <{article.tag}>")
      title = util_xml.GetFirstLeafValByTagName(article, "ArticleTitle") 
      abstracttext = util_xml.GetFirstLeafValByTagName(article, "AbstractText") 
      journal = util_xml.GetFirstLeafValByTagName(article, "Title") 
      year = util_xml.GetFirstLeafValByTagName(article, "Year") 
      pmid = util_xml.GetFirstLeafValByTagName(article, "PMID") 
      if pmid != id_this:
        logging.error(f"PMID {pmid} != {id_this}")
        n_err+=1
        continue
      authorlastname=None;
      #authorlist = article.find("AuthorList") #Why not working?
      if article.iter("AuthorList") is not None and len(list(article.iter("AuthorList")))>0: #Kludge
        authorlist = list(article.iter("AuthorList"))[0] #Kludge
        authors = authorlist.findall("Author")
        for author in authors:
          authorlastname = util_xml.GetFirstLeafValByTagName(author, "LastName")
          break
      df_this = pd.DataFrame({
	"pmid":[pmid],
	"title":[title],
	"abstract":[abstracttext],
	"author":[authorlastname],
	"journal":[journal],
	"year":[year]
	})
      if fout is not None:
        df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      else:
        df = pd.concat([df, df_this])
      n_out+=df_this.shape[0]
    tq.update(n=1)
  tq.close()
  logging.info(f"n_ids: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  return df

#############################################################################
