#!/usr/bin/env python3
##############################################################################
### Medline utilities - access SNOMED and ICD codes
### https://medlineplus.gov/connect/technical.html
### https://medlineplus.gov/connect/service.html
##############################################################################
### https://apps.nlm.nih.gov/medlineplus/services/mpconnect_service.cfm
### Two required parameters:
### 1. Code System (one of): 
###	ICD-10-CM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.90
###	ICD-9-CM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.103
###	SNOMED_CT: mainSearchCriteria.v.cs=2.16.840.1.113883.6.96
###	NDC: mainSearchCriteria.v.cs=2.16.840.1.113883.6.69
###	RXNORM: mainSearchCriteria.v.cs=2.16.840.1.113883.6.88
###	LOINC:	mainSearchCriteria.v.cs=2.16.840.1.113883.6.1
### 2. Code: 
###	mainSearchCriteria.v.c=250.33
###
### Content format:
###	XML (default): knowledgeResponseType=text/xml
###	JSON: knowledgeResponseType=application/json
###	JSONP: knowledgeResponseType=application/javascript&callback=CallbackFunction
###	  where CallbackFunction is a name you give the call back function.
##############################################################################
### Not clear if this API is good.  The text on MedlinePlus web pages such
### as https://medlineplus.gov/druginfo/meds/a697035.html not available via
### API?
##############################################################################
import sys,os,re,time,logging
import urllib.parse,json
#
from ..util import rest
#
CODESYSTEMS = {
	'SNOWMEDCT'	: '2.16.840.1.113883.6.96',
	'ICD9CM'	: '2.16.840.1.113883.6.103',
	'ICD10CM'	: '2.16.840.1.113883.6.90',
	'NDC'		: '2.16.840.1.113883.6.69',
	'RXNORM'	: '2.16.840.1.113883.6.88',
	'LOINC'		: '2.16.840.1.113883.6.1'
	}
#
##############################################################################
def GetCode(base_url, codesys, codes, fout):
  url=base_url
  url+=('?knowledgeResponseType=application/json')
  url+=('&mainSearchCriteria.v.cs='+CODESYSTEMS[codesys])
  for code in codes:
    url_this =url+('&mainSearchCriteria.v.c='+code)
    rval = rest.Utils.GetURL(url_this, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))

##############################################################################
