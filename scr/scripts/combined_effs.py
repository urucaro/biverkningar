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
    subs = {}
    for id in nplids_list:
        subs [id] = drug.Drug (database_obj, id).substances()
    return subs

def search_subtns(subtns):
    """Search in the substances index file for the nplid that contain the substances in subtn_list.
    The input can be a list or a dict where the keys are nplids and the values are substances"""
    with open (os.path.join(database_obj.index_path, 'substances_index.py'),'r') as f:
        output = ast.literal_eval (f.read())
        if isinstance (subtns,  dict):
            result_dict = {}
            for k, value in subtns.iteritems():
                subdict = {}
                for v in value:
                    subdict [v] = [output.get (v)]
                result_dict [k] = [subdict]
            return result_dict
        elif isinstance (subtns,  dict):
            list_result = [output.get (id) for sub in subtns]
            return list_result
        else:
            return None

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

leta_substanser = search_subtns (substanser)

hitta_i_ue = find_match_ue (leta_substanser)
print hitta_i_ue

    
