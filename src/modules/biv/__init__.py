#!/usr/bin/python
#-*- coding:  utf8 -*-

import argparse
import os
from ast import literal_eval
from pprint import pprint


class Configuration (object):
    def __init__(self, p):
        """Reads a configuration file"""
        pass


class Environment (object):
    def __init__ (self,  p):
        """Create an environment based on the prefix 'p'"""
        assert os.path.isdir (p)
        self.prefix = p
        self.data_path = os.path.join (self.prefix, 'data')
        self.index_path = os.path.join (self.data_path,'index')
        self.products_path = os.path.join (self.data_path,'products')
        self.ue_path = os.path.join (self.data_path,'ue')
        self.db_xap_path = os.path.join (self.data_path,'db-xap')
        self.conf = Configuration (self.prefix)


class Database (object):
    """Database holding information about drugs"""
    def __init__(self, x):
        """Initialize the database placed in'x'"""
        assert os.path.isdir (x)
        self.env = Environment (x)
        self.basepath = self.env.prefix
        self.data_path = self.env.data_path
        self.index_path = self.env.index_path
        self.products_path = self.env.products_path
        self.ue_path = self.env.ue_path
        self.db_xap_path = self.env.db_xap_path
        self.ue_match = None
        self.subs_nplids_dict = {}
        self.subs_nplids_dict = {}
        
    def products (self):
        """Returns a list with all the nplids in 'products' db"""
        products_list = []
        for p in self.products_path:
            products_list.append (os.path.splitext (p)[0])
        return products_list

    def has (self,  id):
        """Is there a drug with nplid 'id' in the database"""
        fn = os.path.join (self.products_path,  '%s.py' %id)
        status = os.path.isfile (fn)
        return status

    def drug (self,  id):
        """Returns an instance of the class 'Drug' with nplid 'id' """
        return Drug (self, id)

substances_index = None

class Drug (object):
    """Holding information about atc-code, substances, adverse effects etc"""
    def __init__ (self, db_obj, id):
        assert db_obj.has (id)
        self.id = id
        self.db_obj = db_obj
        self.index_path = db_obj.index_path
        self.products_path = db_obj.products_path
        self.ue_path = db_obj.ue_path
        self.product_fn = os.path.join (self.products_path, '%s.py' %self.id)
        self.load_data ()

    def load_data (self):
        """reads data"""
        with file (self.product_fn)  as f:
            body = f.read ()
            self._data_prod = literal_eval (body)

    def store (self):
        with open (self.product_fn,'w') as f:
            pprint (self._data_prod,  stream = f)

    def atc (self):
        """Gives the atc-code for a given drug with nplid 'id """
        result = self._data_prod.get ('atc_code',  {})
        return result

    def substances (self):
        """A list with the active substance for a given drug with nplid 'id' """
        result = []
        ingredients = self._data_prod.get ('ingredients', {})
        for ingredient in ingredients:
            result.append (self._data_prod.get ('ingredients', {}).get (ingredient,  {}).get ('substance',  {}))
        return result

    def index_siblings (self):
        """Returns a dictionary with the keys being the contained substances and the values the products
        (siblings) that contain that substance,requires that the 'substances_index.py' file has been created"""
        result = {}
        global substances_index
        if not substances_index: 
            with open (os.path.join (self.index_path, 'substances_index.py'),'r') as f:
                substances_index = literal_eval (f.read())
        for sub in self.substances():
            result [sub] = substances_index.get (sub)
        return result

    def write_siblings (self):
        siblings = self.index_siblings () 
        self._data_prod ['siblings'] = siblings 
        self.store ()

    def get_siblings (self):
        """Fetch the key 'siblings' from the products db """
        result = self._data_prod.get ('siblings', '')
        return result
        
    def document_id (self):
        """Get the key 'doc-id' if existent in products db """
        result = self._data_prod.get ('doc-id', '')
        return result

    def undesired_effs (self, key):
        """A list with known undesired effects for drug with nplid 'id' 
        listed in the 'ue' database. 'key' is i.e. common, rare, all etc."""
        doc_id = self.document_id ()
        
        if doc_id:
            filepath = os.path.join (self.ue_path, doc_id + '.py')
            with file (filepath) as f:
                body = literal_eval (f.read ())
                uneffs = body.get ('_data', '')
                if uneffs:
                    uneffs_dict = dict (uneffs)
                if key == 'all':
                    result = uneffs_dict
                else:
                    fixed_key = key[:1].upper() + key[1:].lower()
                    result = uneffs_dict.get (fixed_key, '')
                    if not result:
                        result = 'There are no %s undesired effects' %key
        else:
            result = None
        return result

    def pharmform_dose (self):
        """The pharmaceutical form of the drug,i.e. tablet, injection etc and the dose"""
        pharmform  = self._data_prod.get ('pharma', '').get ('pharmaceutical-form', '')
        dose = self._data_prod.get ('pharma', '').get ('strength-text', '')
        result = pharmform, dose
        return result

    
class UE (object):
    def __init__ (self, drug_obj):
        pass

#-----------------------------------------------------------------------------------------------------------
if __name__=='__main__':#gör att det bara körs om det är huvudprogrammet

    parser = argparse.ArgumentParser('Get information about a drug from its nplid') 

    parser.add_argument('-p' ,'--prefix',  help = 'The path to database')
    parser.add_argument('-n', '--nplid', default = '',  help = 'The nplid of the drug')
    parser.add_argument ('command',  help="Valid actions: test, init-subs")


    args = parser.parse_args()
    if args.prefix:
        database = Database(args.prefix)
        print args.prefix
    else:
        import sys
        parser.error ('You have to give the path to the database') 
        sys.exit (-1)
        
    if args.command =='test':
        if args.nplid:
            try:
                drug_obj = database.drug(args.nplid)
                
                substances = drug_obj.substances()
                effects = drug_obj.undesired_effs('common')
                form = drug_obj.pharmform_dose()
                siblings = drug_obj.get_siblings ()
                doc = drug_obj.get_siblings ()
                
                print substances
                print effects
                print form
                print siblings
            except AssertionError:
                print 'There is no drug with that nplid'
    elif args.command == 'init-subs':
        pass #init_subs (args.prefix)






