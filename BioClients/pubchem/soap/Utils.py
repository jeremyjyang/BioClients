#!/usr/bin/env python3
'''
Utility functions for original SOAP (pre-REST) PUG API.

Jeremy Yang
'''
import sys,os,re,urllib,time,logging
import xml.dom.minidom

from ...util import xml_utils

PUGURL='http://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi'

#############################################################################
def PollPug(reqid,mode='status',pugurl=PUGURL,ntries=20,poll_wait=10):
  qxml='''\
<PCT-Data><PCT-Data_input>
  <PCT-InputData><PCT-InputData_request>
    <PCT-Request>
      <PCT-Request_reqid>%(REQID)d</PCT-Request_reqid>
      <PCT-Request_type value="%(MODE)s"/>
    </PCT-Request>
  </PCT-InputData_request></PCT-InputData>
</PCT-Data_input></PCT-Data>
'''%{'REQID':reqid,'MODE':mode}
  logging.debug('connecting %s...'%pugurl)
  f=UrlOpenTry(pugurl,qxml,ntries,poll_wait)
  pugxml=f.read()
  f.close()
  status,reqid,url,qkey,wenv,error = ParsePugXml(pugxml)

  return status,reqid,url,qkey,wenv,error

#############################################################################
def ParsePugXml(pugxml):
  status,reqid,url,qkey,wenv,error=None,None,None,None,None,None
  try:
    dom=xml.dom.minidom.parseString(pugxml)
  except xml.parsers.expat.ExpatError as e:
    logging.info('XML parse error: %s'%e)
    logging.info('XML: %s'%pugxml)
    sys.exit(1)
  tag='PCT-Status'
  statuss=xml_utils.DOM_GetAttr(dom,tag,'value')
  if statuss: status=statuss[0]
  tag='PCT-Status-Message_message'
  errors=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if errors: error=errors[0]
  tag='PCT-Waiting_reqid'
  reqids=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if reqids: reqid=int(reqids[0])
  tag='PCT-Download-URL_url'
  urls=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if urls: url=urls[0]
  tag='PCT-Entrez_query-key'
  qkeys=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if qkeys: qkey=qkeys[0]
  tag='PCT-Entrez_webenv'
  wenvs=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if wenvs: wenv=wenvs[0]
  return status,reqid,url,qkey,wenv,error

#############################################################################
def UrlOpenTry(url=PUGURL,xml=None,ntries=20,poll_wait=10):
  ### To recover from FTP timeouts:
  fin=None
  for i in range(ntries):
    try:
      if xml:
        fin=urllib.urlopen(url,xml)
      else:
        fin=urllib.urlopen(url)
      break
    except IOError as e:
      logging.info('IOError: %s'%e)
      time.sleep(poll_wait)
  if not fin:
    logging.info('ERROR: failed download, %d tries, quitting...'%ntries)
    sys.exit(1)
  return fin

#############################################################################
def DownloadUrl(url,fout,ntries=20,poll_wait=10):
  fin=UrlOpenTry(url,None,ntries,poll_wait)
  nbytes=0
  while True:
    buff=fin.read(1024)
    if not buff: break
    fout.write(buff)
    nbytes+=len(buff)
  fin.close()
  return nbytes

#############################################################################
### error status values include: "server-error"
#############################################################################
def CheckStatus(status,error):
  if status not in ('success','queued','running'):
    ErrorExit('query failed; quitting (status="%s",error="%s").'%(status,error))

#############################################################################
def ErrorExit(msg):
  logging.info(msg)
  sys.exit(1)
