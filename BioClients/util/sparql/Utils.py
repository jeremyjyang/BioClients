#!/usr/bin/env python3
"""
Sparql endpoint client utility functions
"""
###
import os,sys,re,json,logging

import SPARQLWrapper

#############################################################################
def SparqlRequest(rq_code, rq_uri, defgraph=None, fmt=None):
  rq_results = None
  logging.debug('URI: %s'%(rq_uri))
  logging.debug('%s'%(rq_code))
  try:
    sparql = SPARQLWrapper.SPARQLWrapper(rq_uri)
    sparql.setQuery(rq_code)
    if fmt:
      sparql.setReturnFormat(fmt)
    rq_results = sparql.query()
  except Exception as e:
    logging.error('Error: %s'%e)
    errtype,val,traceback = sys.exc_info()
    logging.error('sys.exc_info:\n(%s)\n%s'%(errtype,val))
    if traceback: logging.info('traceback:\n%s>'%(traceback))
    logging.error('%s'%str(rq_code))
  return rq_results

#############################################################################
def Results2TSV(results, variables, nmax, fout):
  if variables:
    variables = variables.strip()
    variables = re.split(r'[\s,]+', variables)
  else:
    variables=[]
  if not variables:
    variables = results["head"]["vars"]
  logging.debug("selected vars: %s"%(','.join(variables)))
  if "link" in results["head"]:
    logging.debug("links: %s"%(','.join(results["head"]["link"])))
  if "distinct" in results["results"]:
    logging.debug("distinct: %s"%results["results"]["distinct"])
  if "ordered" in results["results"]:
    logging.debug("ordered: %s"%results["results"]["ordered"])
  n_row=0;
  fout.write('%s\n'%('\t'.join(variables)))
  for binding in results["results"]["bindings"]:
    logging.debug(json.dumps(binding, indent=2))
    row_out=[]
    for var in variables:
      if var in binding:
        val = binding[var]["value"]
        if binding[var]["type"]=='uri':
          val=('<%s>'%val)
      else:
        val=''
      try:
        val=val.encode('utf8')
      except:
        logging.info('unicode error [%d]'%n_row)
        val='error'
      row_out.append(val)
    fout.write('%s\n'%('\t'.join(row_out)))
    n_row+=1
    if n_row==nmax:
      logging.info('NOTE: Output truncated at NMAX = %d.'%nmax)
      break
  logging.info('N = %d'%n_row)

#############################################################################
### Return list of rows, each row list of values.
#############################################################################
def Results2List(results, variables, nmax):
  if variables:
    variables = variables.strip()
    variables = re.split(r'[\s,]+', variables)
  else:
    variables=[]
  if not variables:
    variables = results["head"]["vars"]
  logging.debug("selected vars: %s"%(','.join(variables)))
  if "link" in results["head"]:
    logging.debug("links: %s"%(','.join(results["head"]["link"])))
  if "distinct" in results["results"]:
    logging.debug("distinct: %s"%results["results"]["distinct"])
  if "ordered" in results["results"]:
    logging.debug("ordered: %s"%results["results"]["ordered"])
  n_row=0
  results_out=[]
  for binding in results["results"]["bindings"]:
    logging.debug(json.dumps(binding, indent=2))
    row_out=[]
    for var in variables:
      if var in binding:
        val = binding[var]["value"]
        if binding[var]["type"]=='uri':
          val=('<%s>'%val)
      else:
        val=''
      try:
        val=val.encode('utf8')
      except:
        logging.info('unicode error [%d]'%n_row)
        val='error'
      row_out.append(val)
    results_out.append(row_out)
    n_row+=1
    if n_row==nmax:
      logging.info('NOTE: Output truncated at NMAX = %d.'%nmax)
      break

  logging.info('N = %d'%n_row)

  return results_out

#############################################################################
#  FILTER (lang(?propval) = "en" || lang(?propval) = "" ) ##removes depiction
#  FILTER (lang(?propval) IN ( "en" , "" )) ##removes depiction
def Drugname2Sparql(drugname):
  rq_code='''\
SELECT DISTINCT
  ?drug ?propname ?propval
WHERE
{
  {
    <http://dbpedia.org/resource/%(DRUGNAME)s> rdf:type <http://dbpedia.org/ontology/Drug> .
    <http://dbpedia.org/resource/%(DRUGNAME)s> ?propname ?propval .
  }
  UNION
  {
    ?drug rdf:type <http://dbpedia.org/ontology/Drug> .
    ?drug ?propname ?propval .
    { ?drug <http://dbpedia.org/property/licenceEu> ?synonym . }
    UNION
    { ?drug <http://dbpedia.org/property/licenceUs> ?synonym . }
    UNION
    { ?drug <http://dbpedia.org/property/tradename> ?synonym . }
    UNION
    {
      ?drug rdfs:label ?synonym .
      FILTER (regex(?synonym, "^%(DRUGNAME)s$", "i"))
    }
    FILTER (regex(?synonym, "^%(DRUGNAME)s$", "i"))
  }
}
'''%{'DRUGNAME':drugname}
  return rq_code

#############################################################################
def Test(drugname="metformin", fmt=SPARQLWrapper.JSON):
  RQ_URI='http://dbpedia.org/sparql'
  logging.info('drugname: "%s"; endpoint: %s'%(drugname, RQ_URI))
  rq_code = Drugname2Sparql(drugname)
  logging.debug('sparql:\n%s'%(rq_code))
  rq_results = SparqlRequest(rq_code, RQ_URI, defgraph=None, fmt=fmt)
  if fmt in (SPARQLWrapper.JSON, SPARQLWrapper.JSONLD):
    print(json.dumps(rq_results.convert(), indent=2))
  elif fmt in (SPARQLWrapper.XML, SPARQLWrapper.RDFXML, SPARQLWrapper.RDF):
    print(rq_results.convert().toxml())
  else:
    print(rq_results.convert().decode("utf-8"))

#############################################################################
