#!/usr/bin/env python3
"""
Monarch REST utilities.

https://monarchinitiative.org/page/services
https://monarchinitiative.org/docs/files/api-js.html
https://github.com/monarch-initiative/owlsim-v3
https://github.com/monarch-initiative/monarch-analysis

/search	searches over ontology terms via OntoQuest
/autocomplete	proxy for vocbaulary services autocomplete
/disease	disease info or page
/phenotype	phenotype info or page
/simsearch	OwlSim search using search profile of ontology classes

https://monarchinitiative.org/disease/OMIM_127750.json
https://monarchinitiative.org/phenotype/HP_0000003.json
https://monarchinitiative.org/compare/OMIM:270400/NCBIGene:5156,OMIM:249000,OMIM:194050.json

We use OwlSim for semantic matching when comparing two entities (such as genes,
diseases, or genotypes) with sets of attributes (phenotypes). URLs are of the form
/compare/:x/:y.json
where x can be either an entity or a list of phenotypes and y can be a list of
entities and/or sets of phenotypes.
This wraps a call to getGroupwiseSimilarity(x,y) in OwlSim. This works such that
given a query id (such as a gene, genotype, disease), and one or more target
identifiers, it will map each to it's respective phenotypes, and perform an OwlSim
comparison of the query to each target. You are permitted to mix query and target
types. For example, your query can be a disease, and the target(s) be a list of
gene(s), disease(s), phenotype(s), and/or genotype(s). You can indicate to union the
phenotypes of either the query or the target with a plus "+". Only one entity may be
supplied for the query, whereas multiple target entities are allowed (delimited by a
comma).  For details on owlsim, see http://owlsim.org

Paths:
/compare/:id1/:id2
/compare/:id1/:id2,id3,...idN
/compare/:id1+:id2/:id3,:id4,...idN
/compare/:id1/:id2+:id3,:id4,:id5+:id6,...,:idN

IC = Information Content
LCS = Least Common Subsumers
See OwlSim docs and pubs.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3653101/
"""
###
import sys,os,re,json,logging
import pandas as pd
import urllib,urllib.parse
#
from ..util import rest
#
API_HOST="monarchinitiative.org"
API_BASE_PATH=""
BASE_URL = "https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def GetDisease(ids, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  for id_this in ids:
    disease = rest.GetURL(f"{base_url}/disease/{id_this}.json", parse_json=True)
    logging.debug((json.dumps(disease, indent=2, sort_keys=False)))
    if not tags:
      tags = list(disease.keys())
      for tag in ("relationships", "equivalentNodes", "equivalentClasses", "bundleJS", "bundleCSS"):
        tags.remove(tag)
    df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
  logging.info(f"IDs in: {len(ids)}; n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

##############################################################################
def GetDiseaseRelationships(ids, base_url=BASE_URL, fout=None):
  tags_dis=[]; tags_rel=[]; df=pd.DataFrame();
  for id_this in ids:
    disease = rest.GetURL(f"{base_url}/disease/{id_this}.json", parse_json=True)
    logging.debug((json.dumps(disease, indent=2, sort_keys=False)))
    if not tags_dis:
      for tag in disease.keys():
        if type(disease[tag]) not in (list, dict): tags_dis.append(tag)
    rels = disease["relationships"] if "relationships" in disease else []
    for rel in rels:
      if not tags_rel:
        tags_rel = list(rel.keys())
      df_this = pd.concat([
        pd.DataFrame({tags_dis[j]:[disease[tags_dis[j]]] for j in range(len(tags_dis))}),
        pd.DataFrame({tags_rel[j]:[rel[tags_rel[j]]] for j in range(len(tags_rel))}) ], axis=1)
      df = pd.concat([df, df_this], axis=0)
  logging.info(f"IDs in: {len(ids)}; n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

##############################################################################
def GetPhenotype(ids, base_url=BASE_URL, fout=None):
  return

##############################################################################
def GetGene(ids, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  for gid in ids:
    gene = rest.GetURL(f"{base_url}/gene/{gid}.json", parse_json=True)
    logging.debug((json.dumps(gene, indent=2, sort_keys=False)))
    if not tags: tags = list(gene.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[gene[tags[j]]] for j in range(len(tags))})])
  logging.info(f"IDs in: {len(ids)}; n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

##############################################################################
### Guess: The matches each consist of a 3-tuple,
###	A = phenotype in profileA,
###	B = phenotype in profileB, and
###	LCS = Least Common Subsumers phenotype in...
### EPO?  (But we see MP, ZP, HP...)
##############################################################################
def ComparePhenotypes(idAs, idBs, base_url=BASE_URL, fout=None):
  tags=[]; df=pd.DataFrame();
  #fout.write("idA,typeA,labelA,taxonA,idB,typeB,labelB,taxonB,url,matchidA,matchlabelA,matchidB,matchlabelB,matchidLCS,matchlabelLCS,matchicA,matchicB,matchicLCS\n")
  for idA in idAs:
    url_this = f"{base_url}/compare/{idA}/{(','.join(idBs))}.json"
    rval = rest.GetURL(url_this, parse_json=True)
    logging.debug(json.dumps(rval, indent=2, sort_keys=False))
    cmpr = rval
    if not tags: tags = list(cmpr.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[cmpr[tags[j]]] for j in range(len(tags))})])

#    A = cmpr["a"] if "a" in cmpr else {}
#    typeA = A["type"] if "type" in A else ""
#    idAx = A["id"] if "id" in A else ""
#    labelA = A["label"] if "label" in A else ""
#    taxonA = A["taxon"]["id"] if ("taxon" in A and "id" in A["taxon"]) else {}
#    logging.info("A[type]: "%s" ; A[id]: "%s" ; A[label]: "%s""%(typeA, idA, labelA))
#    resource = cmpr["resource"] if "resource" in cmpr else {}
#    for key in resource.keys():
#      logging.info("resource[%s]: %s"%(key,resource[key]))
#    metadata = cmpr["metadata"] if "metadata" in cmpr else {}
#    for key in metadata.keys():
#      logging.info("metadata[%s]: %s"%(key,str(metadata[key])))
#    Bs = cmpr["b"] if "b" in cmpr else []
#    for B in Bs:
#      labelB = B["label"] if "label" in B else ""
#      typeB = B["type"] if "type" in B else ""
#      idB = B["id"] if "id" in B else ""
#      logging.info('B[type]: "%s" ; B[id]: "%s" ; B[label]: "%s"'%(typeB, idB, labelB))
#      bscore = B["score"] if "score" in B else {}
#      taxonB = B["taxon"]["id"] if ("taxon" in B and "id" in B["taxon"]) else {}
#      matches = B["matches"] if "matches" in B else []
#      vals_ab=[idA,typeA,labelA,taxonA,idB,typeB,labelB,taxonB,url_this]
#      for m in matches:
#        n_match+=1
#        mA = m["a"] if "a" in m else {}
#        matchidA = mA["id"] if "id" in mA else ""
#        matchlabelA = mA["label"] if "label" in mA else ""
#        mB = m["b"] if "b" in m else {}
#        matchidB = mB["id"] if "id" in mB else ""
#        matchlabelB = mB["label"] if "label" in mB else ""
#        mLCS = m["lcs"] if "lcs" in m else {}
#        matchidLCS = mLCS["id"] if "id" in mLCS else ""
#        matchlabelLCS = mLCS["label"] if "label" in mLCS else ""
#        matchicA = mA["IC"] if "IC" in mA else "" #same as LCS?
#        matchicB = mB["IC"] if "IC" in mB else "" #same as LCS?
#        matchicLCS = mLCS["IC"] if "IC" in mLCS else ""
#        vals_this=vals_ab+[matchidA,matchlabelA,matchidB,matchlabelB,matchidLCS,matchlabelLCS,matchicA,matchicB,matchicLCS]
#        fout.write("\t".join([str(val) for val in vals_this])+"\n")
#        n_out+=1

  logging.info(f"n_comparison = {len(idAs)*len(idBs)} ({len(idAs)}x{len(idBs)})")
  #logging.info("n_match = {n_match}; n_out = {n_out}")
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

##############################################################################
