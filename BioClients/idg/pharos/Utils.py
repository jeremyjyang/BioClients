#!/usr/bin/env python3
"""
Pharos  GraphQL API client

Depends on package python-graphql-client.
"""
###
import sys,os,json,re,time,logging
#
from python_graphql_client import GraphqlClient
#
# curl 'https://pharos-api.ncats.io/graphql' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Connection: keep-alive' -H 'DNT: 1' -H 'Origin: https://pharos-api.ncats.io' --data-binary '{"query":"query targetDetails {\n  target(q: { sym: \"ACE2\" }) {\n    name\n    tdl\n    fam\n    sym\n    description\n    novelty\n  }\n}\n"}' --compressed
#
API_ENDPOINT="https://pharos-api.ncats.io/graphql"
#
API_HEADERS = { 'Accept-Encoding': 'gzip, deflate, br',
	'Content-Type': 'application/json', 'Accept': 'application/json',
	'Connection': 'keep-alive', 'DNT': '1',
	'Origin': 'https://pharos-api.ncats.io' }
#
IDTYPES_TARGET = {
	'tcrdid':{'type':'Int'},
	'uniprot':{'type':'String'},
	'sym':{'type':'String'},
	}
IDTYPES_DISEASE = {
	'cui':{'type':'String'},
	'doid':{'type':'String'},
	'name':{'type':'String'},
	}
#
#############################################################################
def GetTargets(ids, idtype, ep=API_ENDPOINT, fout=None):
  tags=[]; n_out=0;
  client = GraphqlClient(endpoint=ep, verify=True)
  query = f"""\
query targetDetails($id: {IDTYPES_TARGET[idtype]['type']}) {{
  target(q: {{ {idtype}: $id }}) {{
    name
    tdl
    fam
    sym
    tcrdid
    uniprot
    description
    novelty
  }}
}}
"""

  for id_this in ids:
    logging.debug(f"id_this: {id_this}")
    variables = { "id": int(id_this) if IDTYPES_TARGET[idtype]['type']=='Int' else id_this }
    try:
      data = client.execute(query=query, variables=variables, headers=API_HEADERS)
    except Exception as e:
      logging.error(e)
      continue
    print(json.dumps(data, indent=2))
    n_out+=1
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")

#############################################################################
def GetDiseases(ids, idtype, ep=API_ENDPOINT, fout=None):
  tags=[]; n_out=0;
  client = GraphqlClient(endpoint=ep, verify=True)
  query = f"""\
query diseaseDetails($id: String) {{
  disease(name: $id) {{
    name
    dids {{ id, doName, dataSources, doDefinition }}
    doDescription
    uniprotDescription
    children {{
      name
      dids {{ id, doName, dataSources, doDefinition }}
      doDescription
    }}
    targetCounts {{
      name
      value
    }}
  }}
}}
"""

  for id_this in ids:
    logging.debug(f"id_this: {id_this}")
    variables = { "id": id_this }
    try:
      data = client.execute(query=query, variables=variables, headers=API_HEADERS)
    except Exception as e:
      logging.error(e)
      continue
    print(json.dumps(data, indent=2))
    n_out+=1
  logging.info(f"n_in: {len(ids)}; n_out: {n_out}")

#############################################################################
def Test(ep=API_ENDPOINT, fout=None):
  client = GraphqlClient(endpoint=ep, verify=True)
  query = """\
query diseaseDetails {{
  disease {{
    name
    dids {{
      id(id:"DOID:2841"), doName
    }}
    doDescription
    uniprotDescription
"""
  try:
    data = client.execute(query=query, headers=API_HEADERS)
  except Exception as e:
    logging.error(e)
    return
  print(json.dumps(data, indent=2))

