#!/usr/bin/python
#-*- coding:  utf8 -*-

import biv
import os
import argparse
import ast
from pprint import pprint
import glob


def init_subs_index (database):
    """Creates a file containing a dictionary where the keys are substances and
    the values are the products (nplids) that contain them"""
    count = 0
    subs_nplids = {}
    for p in os.listdir (database.products_path):
        current_nplid = os.path.splitext (p)[0]
        current_drug = database.drug (current_nplid)
        current_subs = current_drug.substances()
        for sub in current_subs:
            if not sub in subs_nplids:
               subs_nplids [sub] =[]
            subs_nplids [sub] += [current_nplid]
        count += 1
        print count
    with open (os.path.join (database.index_path, 'substances_index.py'), 'wt') as out:
        pprint(subs_nplids, stream=out)

def insert_doc_id (database):
    """If the nplid can be found in the ue database it inserts a key 'doc-id' with the document name from
    the ue dir"""
#    count = 0
    paths = glob.glob (database.ue_path + '/*.py')
    for path in paths:
        basename = os.path.basename (path)
        document_id = os.path.splitext (basename) [0]
        with file (path,  'r') as f:
            body = ast.literal_eval (f.read ())
            nplids = body.get ('__nplids')
            if nplids:
                for id in nplids:
                    drug = database.drug (id)
                    current_doc_id = drug._data_prod.get ('doc-id', '')
                    if current_doc_id:
                        if current_doc_id !=  document_id:
                            print current_doc_id,  document_id
                    else:
                        drug._data_prod ['doc-id'] = document_id
                        drug.store ()
#        count += 1
#        print count # It seems like the count takes time

def products_siblings (database):
    """Inserts a key 'sibings' to each product in the product db, the value is a
    dictionary where the keys are the substances contained by that product
    and the values other products that share that substance """
    count = 0
    for p in os.listdir (database.products_path):
        drug = database.drug (os.path.splitext(p)[0])
        drug.write_siblings ()
        count += 1
        print count
    

#-----------------------------------------------------------------------------------------------------------
if __name__=='__main__':#gör att det bara körs om det är huvudprogrammet

    parser = argparse.ArgumentParser('Maintain the products database') 

    parser.add_argument('-p' ,'--prefix',  help = 'The path to database')
    parser.add_argument ('command',  help = "Valid actions: subs-index, doc-id, siblings")


    args = parser.parse_args ()
    if args.prefix:
        environment = biv.Environment (args.prefix)
        database_obj = biv.Database (args.prefix)
        print args.prefix
    else:
        import sys
        parser.error ('You have to give the path to the database')
        sys.exit (-1)
    if args.command == 'subs-index':
        init_subs_index (database_obj)
    elif args.command =='doc-id':
        insert_doc_id (database_obj)
    elif args.command == 'siblings':
        products_siblings (database_obj)
    

    
