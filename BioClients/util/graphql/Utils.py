#!/usr/bin/env python3
###
import sys,os,json,logging

import gql
from gql.transport.requests import RequestsHTTPTransport

#############################################################################
def RunQuery(gql_url, graphql, fout):
  if graphql is None:
    logging.error("No query.")
    return

  _transport = RequestsHTTPTransport(gql_url)
  client = gql.Client(transport=_transport, fetch_schema_from_transport=False)
  logging.debug(f"client.schema: '{client.schema}'")

  try:
    query = gql.gql(graphql)
    rval = client.execute(query)
    fout.write(json.dumps(rval, indent=2)+"\n")
  except Exception as e:
    logging.error(e)

#############################################################################


