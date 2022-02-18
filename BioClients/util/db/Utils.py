#!/usr/bin/env python3
'''
Commonly used functions for database client applications.
'''
import sys,os,logging,urllib.parse
import sqlalchemy

##############################################################################
def PostgreSqlConnect(dbhost, dbport, dbname, dbusr, dbpw):
  import psycopg2
  engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
  return engine.connect()

##############################################################################
def MySqlConnect(dbhost, dbport, dbname, dbusr, dbpw):
  try:
    # pip install MySQL-python
    # import mysql-python #default
    engine = sqlalchemy.create_engine(f"mysql://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
  except:
    try:
      # pip install mysql-connector-python
      # import mysql-connector-python
      engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
    except:
      try:
        # pip install PyMySQL
        # import pymysql
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
      except:
        try:
          # pip install MySQLdb
          # import MySQLdb
          engine = sqlalchemy.create_engine(f"mysql+mysqldb://{dbusr}:{urllib.parse.quote_plus(dbpw)}@{dbhost}:{dbport}/{dbname}")
        except:
          logging.error("Failed to connect.")
          return None

  return engine.connect()
