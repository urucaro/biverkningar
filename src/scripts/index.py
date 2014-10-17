#!/usr/bin/python
#-*- coding:  utf8 -*-

import argparse
import biv
import os
import xapian
import glob
from ast import literal_eval


def index (ue_path, db_xap_path):
    count = 0
    
    # create or open the the database
    db = xapian.WritableDatabase(db_xap_path, xapian.DB_CREATE_OR_OPEN)

    # set up a termgenerator thats going to be used in indexing
    termgenerator = xapian.TermGenerator()
    termgenerator.set_stemmer(xapian.Stem("swedish"))
    
    paths = glob.glob (ue_path + '/*.py')
    for path in paths:
        s_doc_id = os.path.splitext (os.path.basename(path)) [0]
        doc_id =  unicode (s_doc_id,'utf-8')
        with file (path) as f:
            body = literal_eval (f.read ())
        data = body.get ('_data')
        for dat in data:
            frequency = dat [0]
            frequency_joint = '"' + frequency + '"'
            for d in dat [1]:
                system = d [0]
                system_joint = '"' + system+ '"'
                content = d [1]
#                content = unicode (s_content,'utf-8')
                identifier = '%s-ue-%s-%s' %(doc_id,  frequency, system)
                # We make a document and tell the term generator to use this.
                doc = xapian.Document()
                termgenerator.set_document(doc)
                
                # Store all the fields for display purposes.
                doc.set_data (content)
                
                # Index each field with a suitable prefix.
                termgenerator.index_text(frequency_joint, 1, 'XF')
                termgenerator.index_text(system_joint, 1, 'XS')
                
                # Index fields without prefixes for general search.
                termgenerator.index_text(frequency)
                termgenerator.increase_termpos()
                termgenerator.index_text(system)
                termgenerator.increase_termpos()
                termgenerator.index_text(content)
                
                
                
                # We use the identifier to ensure each object ends up in the
                # database only once no matter how many times we run the
                # indexer.
                idterm = u"Q" + identifier
                doc.add_boolean_term(idterm)
                db.replace_document(idterm, doc)
                
                count +=1
                print count

#-----------------------------------------------------------------------------------------------------------
if __name__=='__main__':#gör att det bara körs om det är huvudprogrammet

    parser = argparse.ArgumentParser('Index the drug data') 

    parser.add_argument('-p' ,'--prefix',  help = 'The path to database')
    parser.add_argument ('command',  help="Valid actions: index")


    args = parser.parse_args()
    if args.prefix:
        database = biv.Database (args.prefix)
        db_xap_path =  database.db_xap_path
        ue_path = database.ue_path
        print args.prefix
    else:
        import sys
        parser.error ('You have to give the path to the database') 
        sys.exit (-1)
        
    if args.command =='index':
        index (ue_path, db_xap_path)
        
        
        
        
        
        
