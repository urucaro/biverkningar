#!/usr/bin/python
#-*- coding:  utf8 -*-

import argparse
import os
import ast
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
        self.index_path = os.path.join (self.prefix, 'index')
        self.products_path = os.path.join (self.prefix, 'products')
        self.ue_path = os.path.join (self.prefix, 'ue')
        self.conf = Configuration(self.prefix)


class Database (object):
    """Database holding information about drugs"""
    def __init__(self, x):
        """Initialize the database placed in'x'"""
        assert os.path.isdir (x)
        self.env = Environment (x)
        self.basepath = self.env.prefix
        self.index_path = self.env.index_path
        self.products_path = self.env.products_path
        self.ue_path = self.env.ue_path
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

    def load_ue_matches (self):
        """A dictionary with all the nplids (key) in 'products' database that can be found in the
        'ue' database with product names (value)"""
        if not self.ue_match:
            result = {}            
            for n in os.listdir (self.ue_path):
                ue_filename = os.path.join (self.ue_path, '%s' %n)
                with file (ue_filename) as f:
                    body = ast.literal_eval (f.read ())
                if '__nplids' in body:
                    nplids = body.get('__nplids', {})
                    for k in nplids:
                        result [k] = n
            self.ue_match = result
        return self.ue_match

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
            self._data_prod = ast.literal_eval (body)
        
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
        for k in self._data_prod.get ('ingredients', {}):
            result.append (self._data_prod.get ('ingredients', {}).get (k,  {}).get ('substance',  {}))
        return result

    def siblings (self):
        """Returns a dictionary with the keys being the contained substances and the values the products
        (siblings) that contain that substance"""
        result = {}
        global substances_index
        if not substances_index: 
            with open (os.path.join (self.index_path, 'substances_index.py'),'r') as f:
                substances_index = ast.literal_eval (f.read())
        for sub in self.substances():
            result [sub] = substances_index.get (sub)
        return result

#    def ue_match (self):
#        """returns the corresponding file in the 
#        undesired effects (ue) database if it exist, else returns None"""
#        ue_filename = ''
#        ue_basename = self.db_obj.load_ue_matches ().get (self.id)#Fråga far: Är det ok att sätta ett nytt namn på en dict som redan finns?dvs. skall men undvika att ta upp en massa plats med olika variabler som innhåller samma data
#        if ue_basename:
#            ue_filename = os.path.join (self.ue_path,  ue_basename)
#        return ue_filename

    def undesired_effs (self, key):
        """A list with known undesired effects for drug with nplid 'id' 
        listed in the 'ue' database. 'key' is i.e. common, rare, all etc."""
        result = None
        ue_filename = self.ue_match_fn () #returns a filename if there is a match in 'ue'
        if ue_filename:
            with os.path.join (self.ue_path,  ue_filename) as f:
                body = ast.literal_eval (f.read) 
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
        return result

    def pharmform_dose (self):
        """The pharmaceutical form of the drug,i.e. tablet, injection etc and the dose"""
        pharmform  = self._data_prod.get ('pharma', '').get ('pharmaceutical-form', '')
        dose = self._data_prod.get ('pharma', '').get ('strength-text', '')
        result = pharmform, dose
        return result







#def init_subs (prefix):
#    """Creates a dictionary where the keys are substances and the values are 
#    the products (nplids) that contain that substance"""
#    count = 0
#    db = Database (prefix)
#    subs_nplids = {}
#    for f in os.listdir (db.products_path):
#        current_nplid = os.path.splitext (f)[0]
#        current_drug = Drug(db, current_nplid)
#        current_subs = current_drug.substances()
#        for sub in current_subs:
#            if not sub in subs_nplids:
#               subs_nplids [sub] =[]
#            subs_nplids [sub] += [current_nplid]
#        count += 1
#        print count
#    subs_nplids
#    with open (os.path.join (db.index_path, 'substances_index.py'), 'wt') as out:
##        out.write (str(subs_nplids))
#        pprint(subs_nplids, stream=out)
    


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
                substances = database.drug(args.nplid).substances()
                match = database.drug(args.nplid).ue_match_fn()
                effects = database.drug(args.nplid).undesired_effs('common')
                form = database.drug(args.nplid).pharmform_dose()
                match_dict = database.load_ue_match()
        
                print substances
                print match
                print effects
                print form
            except AssertionError:
                print 'There is no drug with that nplid'
    elif args.command == 'init-subs':
        pass #init_subs (args.prefix)






