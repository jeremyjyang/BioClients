#!/usr/bin/env python3
'''
Commonly used functions for database client applications.
'''
import sys,os,logging,urllib.parse
import sqlalchemy

##############################################################################
def PostgreSqlConnect(dbhost, dbport, dbname, dbusr, dbpw):
  try:
    import psycopg2
    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
  except Exception as e:
    logging.info(f"{e}")
    logging.error("Failed to connect.")
    return None
  return engine.connect()

##############################################################################
def MySqlConnect(dbhost, dbport, dbname, dbusr, dbpw):
  try:
    # https://pypi.org/project/mysql-connector-python/
    # pip install mysql-connector-python
    import mysql.connector
    engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
  except Exception as e:
    logging.info(f"{e}")
    try:
      # https://pypi.org/project/PyMySQL/
      # pip install PyMySQL
      import pymysql
      engine = sqlalchemy.create_engine(f"mysql+pymysql://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
    except Exception as e:
      logging.info(f"{e}")
      try:
        # https://mysqlclient.readthedocs.io/
        # pip install mysqlclient
        import MySQLdb
        engine = sqlalchemy.create_engine(f"mysql+mysqldb://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
      except Exception as e:
        logging.info(f"{e}")
        logging.error("Failed to connect.")
        return None
  return engine.connect()
