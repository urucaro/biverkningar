#!/usr/bin/python
#-*- coding:  utf8 -*-

import drug
import os
import ast

database_prefix = ('/home/carolina/proj/biv/data')
database_obj = drug.Database (database_prefix)

"""Input is a list with nplids, a new list with all the drugs found in the
    database with the same active ingrediens is compiled. The nplids
    in the new list is then compared with with the 'ue' db and the undesired
    effects are extracted   """
    
nplids_list = ['19351204000012', '19651117000025']


#        with open (os.path.join(database_obj.index_path, 'substances_index.py'),'r') as f:
#        output = ast.literal_eval (f.read())
#        for id in nplids_list:
#            substances = output.get (id)


def subtns_list (nplids_list):
    """A dict where the keys are the nplids and the values are the substances they contain"""
    result = {}
    for id in nplids_list:
        result [id] = drug.Drug (database_obj, id).substances()
    return result
    
def containing_products(substances):
    """Given a list of substances it returns a dictionary with values that are nplids of products that 
    contain that substance"""
    assert isinstance (substances, list)
    result = {}
    with open (os.path.join(database_obj.index_path, 'substances_index.py'),'r') as f:
        output = ast.literal_eval (f.read())
        for sub in substances:
            result [sub] = output.get (sub)
    return result

def search_sibling_prod(nplid_subs_dict):
    """Input a dictionary with key 'nplid' and values that are a list with contained substances, 
    each substance becomes a key in a subdict with values that are lists with product which contain 
    that substance"""
    result = {}
    for k, value in nplid_subs_dict.iteritems():
        subdict = {}
        for v in value:
            cont_prod = containing_products ([v])
            subdict [v]= cont_prod [v]
        result [k]=  subdict
    return result

def find_match_ue (nplid_list):
    """finds corresponding drugs in the ue database if existent """
    result = []
    for id in nplid_list:
        drug_obj = drug.Drug (database_obj, id)
        match = drug_obj.ue_match_fn ()
        if match:
            result.append(id)
    return result

def undesired_effs(nplids_list,  key):
    """A list with known undesired effects for the drugs with nplids 'nplid_list',
    'key' is i.e. common, rare, all etc."""
    result = []
    for id in nplids_list:
        drug_obj = drug.Drug (database_obj, id)
        result.append (drug_obj.undesired_effs(key))
    return result
    

substanser = subtns_list (nplids_list)
print substanser

leta_substanser = search_sibling_prod (substanser)
print leta_substanser

hitta_i_ue = find_match_ue (leta_substanser)
print hitta_i_ue

    
