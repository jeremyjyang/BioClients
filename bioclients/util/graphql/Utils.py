#!/usr/bin/env python3
###
# https://gql.readthedocs.io/en/stable/
# https://gql.readthedocs.io/en/stable/usage/basic_usage.html
###
import sys,os,json,logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

#############################################################################
def RunQuery(graphql, base_url, fout):
  if graphql is None:
    logging.error("No query.")
    return

  transport = AIOHTTPTransport(url=base_url)
  client = Client(transport=transport, fetch_schema_from_transport=True)
  logging.debug(f"client.schema: '{client.schema}'")

  try:
    query = gql(graphql)
    result = client.execute(query)
    fout.write(json.dumps(result, indent=2)+"\n")
  except Exception as e:
    logging.error(e)

#############################################################################


