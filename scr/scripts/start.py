#!/usr/bin/python
#-*- coding:  utf8 -*-

import argparse
import os
import ast

class Environment (object):
    def __init__ (self,  p):
        """Create an environment based on the prefix 'p'"""
        assert os.path.isdir (p)
        self.prefix = p
                
        
class Database (object):
    """Database holding information about drugs"""
    def __init__(self, x):
        """Initialize the database placed in'x'"""
        assert os.path.isdir (x)
        self.env = Environment (x)
        self.basepath = self.env.prefix
        self.index_path = os.path.join (self.basepath, 'index')
        self.products_path = os.path.join (self.basepath, 'products')
        self.ue_path = os.path.join (self.basepath, 'ue')
        
#    def filepath (self,  id):
#        """The path to the drug with nplid 'id"""
#        fn = os.path.join (self.products, '%s.py' % id)
#        return fn


    def has (self,  id):
        """Is there a drug with nplid 'id' in the database"""
        fn = os.path.join (self.products_path,  '%s.py' %id)
        status = os.path.isfile (fn)
        return status

    def drug (self,  id):
        """Returns an instance of the class 'Drug' with nplid 'id' """
        assert self.has (id)
        return Drug (self, id)




class Drug (object):
    """Holding information about atc-code, substances, adverse effects etc"""
    def __init__ (self, db_obj, id):
        assert db_obj.has (id)
        self.id = id
        self.db_obj = db_obj
        self.index_path = db_obj.index_path
        self.products_path = db_obj.products_path
        self.ue_path = db_obj.ue_path


    def read_file (self, fn):
        """reads a file 'fn', evaluates and returns the content"""
        with file (fn)  as f:
            body = f.read ()
            result = ast.literal_eval (body)
        return result

    
    def atc (self,  id):
        """Gives the atc-code for a given drug with nplid 'id """
        assert self.db_obj.has (id)
        fn = os.path.join (self.products_path, '%s.py' %id)
        body = self.read_file (fn)
        result = body ['atc_code']
        return result


    def substances (self, id):
        """A list with the active substance for a given drug with nplid 'id' """
        assert self.db_obj.has (id)
        fn = os.path.join (self.products_path, '%s.py' %id)
        body = self.read_file (fn)
        result = []
        for k in body ['ingredients']:
            result.append (body ['ingredients'][k]['substance'])
        return result


    def match_drug (self, id):
        """Given a nplid as 'id' returns the corresponding file in the 
        undesired effects (ue) database if it exist, else returns None"""
        assert self.db_obj.has (id)
        result = None
        
        for n in os.listdir (self.ue_path):
            fn = os.path.join (self.ue_path, n)
            body = self.read_file (fn)
            
            if '__nplids' in body:
                nplids = body ['__nplids']
                for k in nplids:
                    if k == id:
                        result = fn
        return result



    def undesired_effs (self, id, key):
        """A list with known undesired effects for drug with nplid 'id' 
        listed in the ue database"""
        key = key.lower()
        result = None
        
        fn = self.match_drug (id) #returns a filename if there is a match in 'ue'
        if not fn == None:
            body = self.read_file (fn)
            if '_data' in body:
               uneffs = body ['_data']
           
            uneffs_dict = {}
            for eff in uneffs:
                uneffs_dict [eff[0].lower()] = eff [1:]
        
        if key == 'all':
            result = uneffs_dict
        else:
            try:
                result = uneffs_dict [key]
            except KeyError:
                result = 'There are no %s undesired effects' %key
        
        return result
        
    def pharmform (self, id):
        """The pharmaceutical form of the drug: tablet injection etc"""
        fn = os.path.join (self.products_path, '%s.py' %id)
        body = self.read_file (fn)
        try:
            result = body ['pharma']['pharmaceutical-form']
        except KeyError:
            result = None
        return result
        
            
            
        
        
        














#-----------------------------------------------------------------------------------------------------------
if __name__=='__main__':#gör att det bara körs om det är huvudprogrammet

    parser = argparse.ArgumentParser('Get information about a drug from its nplid') 
    
    parser.add_argument('-p' ,'--prefix',  help = 'The path to database')
    parser.add_argument('-n', '--nplid', default = '',  help = 'The nplid of the drug')
    
    
    args = parser.parse_args()
    if args.prefix:
        database = Database(args.prefix)
        print args.prefix
        if args.nplid:
            try:
                substances = database.drug(args.nplid).substances(args.nplid)
                match = database.drug(args.nplid).match_drug(args.nplid)
                effects = database.drug(args.nplid).undesired_effs(args.nplid, 'common')
                form = database.drug(args.nplid).pharmform(args.nplid)
                
                print substances
                print match
                print effects
                print form
            except AssertionError:
                print 'There is no drug with that nplid'
    elif not args.prefix:
        parser.error ('You have to give the path to the database') 
        
         
        

    
    
    
