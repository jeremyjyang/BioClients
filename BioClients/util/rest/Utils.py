#!/usr/bin/env python3
'''
Commonly used functions for REST client applications.

* JSON and XML handled, parsed into objects.
* HTTP headers and POST data handled.

'''
import sys,os,io,re,time,logging,base64,json
import urllib,urllib.request,urllib.parse
from xml.etree import ElementTree as ET
#
REST_TIMEOUT=10
REST_RETRY_NMAX=10
REST_RETRY_WAIT=5
#
##############################################################################
def GetURL(url, headers={}, parse_json=False, usr=None, pw=None, parse_xml=False, nmax_retry=REST_RETRY_NMAX, verbose=0):
  '''Entry point for GET requests.'''
  return RequestURL(url, headers, None, usr, pw, parse_json, parse_xml, nmax_retry, verbose)

##############################################################################
def PostURL(url, headers={}, data={}, usr=None, pw=None, parse_json=False, parse_xml=False, nmax_retry=REST_RETRY_NMAX, verbose=0):
  '''Entry point for POST requests.'''
  return RequestURL(url, headers, data, usr, pw, parse_json, parse_xml, nmax_retry, verbose)

##############################################################################
def RequestURL(url, headers, data, usr, pw, parse_json, parse_xml, nmax_retry, verbose):
  '''Use internally, not externally.  Called by GetURL() and PostURL().  Only Basic authentication supported.'''
  if data and type(data) is dict:
    data = urllib.parse.urlencode(data).encode('utf-8')
  elif data and type(data) in (str,): #Ok for SOAP/XML?
    data = data.encode('utf-8')
  else:
    data = None
  req = urllib.request.Request(url=url, headers=headers, data=data)
  if usr and pw:
    req.add_header("Authorization", "Basic %s"%base64.encodestring('%s:%s'%(usr,pw)).replace('\n','')) 

  logging.debug('url="%s"'%url)
  logging.debug('request type = %s'%req.type)
  logging.debug('request method = %s'%req.get_method())
  logging.debug('request host = %s'%req.host)
  logging.debug('request full_url = %s'%req.full_url)
  logging.debug('request header_items = %s'%req.header_items())
  if data:
    logging.debug('request data = %s'%req.data)
    logging.debug('request data size = %s'%len(req.data))

  i_try=0
  while True:
    i_try+=1
    try:
      with urllib.request.urlopen(req, timeout=REST_TIMEOUT) as f:
        fbytes = f.read() #With Python3 read bytes from sockets.
        ftxt = fbytes.decode('utf-8')
        #f.close()
    except urllib.request.HTTPError as e:
      if e.code==404:
        return ([])
      elif e.code==400:
        logging.warn('%s (URL=%s)'%(e, url))
      else:
        logging.warn('%s'%e)
      return None
    except urllib.request.URLError as e:  ## may be socket.error
      # may be "<urlopen error [Errno 110] Connection timed out>"
      logging.warn('[try %d/%d]: %s'%(i_try, nmax_retry, e))
      if i_try<nmax_retry:
        time.sleep(REST_RETRY_WAIT)
        continue
      return None
    except Exception as e:
      logging.warn('%s'%e)
      if i_try<nmax_retry:
        time.sleep(REST_RETRY_WAIT)
        continue
      return None
    break

  if ftxt.strip()=='': return None
  #logging.debug('%s'%ftxt)

  if parse_json:
    try:
      rval = json.loads(ftxt, encoding='utf-8')
    except ValueError as e:
      logging.debug('JSON Error: %s'%e)
      try:
        ### Should not be necessary.  Backslash escapes allowed in JSON.
        ftxt_fix = ftxt.replace(r'\"', '&quot;').replace(r'\\', '')
        ftxt_fix = ftxt_fix.replace(r'\n', '\\\\n') #ok?
        rval = json.loads(ftxt_fix, encoding='utf-8')
        logging.debug('Apparently fixed JSON Error: %s'%e)
        logging.debug('Apparently fixed JSON: "%s"'%ftxt)
      except ValueError as e:
        logging.error('Failed to fix JSON Error: %s'%e)
        logging.error('ftxt_fix="%s"'%ftxt_fix)
        raise
  elif parse_xml:
    try:
      rval = ParseXml(ftxt)
    except Exception as e:
      logging.error('XML Error: %s'%e)
      rval=ftxt
  else: #raw
    rval=ftxt

  return rval

#############################################################################
def ParseXml(xml_str):
  """ElementTree.fromstring() returns root Element. ElementTree.parse() returns ElementTree."""
  etree=None;
  try:
    etree = ET.parse(io.StringIO(xml_str))
  except Exception as e:
    logging.warn('XML parse error: %s'%e)
    return False
  return etree

#############################################################################
