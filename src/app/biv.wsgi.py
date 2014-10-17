#!/usr/bin/python
#-*- coding:  utf8 -*-


import bottle
import biv
import os
import sys

def template (tpl_type):
    result_tpl = os.path.join(tpl_dir,tpl_type +'.tpl')
    assert os.path.isfile(result_tpl)
    return result_tpl

def accept (req):
    accepted = dict (req)['HTTP_ACCEPT']
    if 'json' in accepted:
        return 'json'
    else:
        return 'html'

def output_representation (data,  acc, tpl = None, other = {}):
    if acc == 'json':
        return repr(data)
    elif acc == 'html':
        assert tpl   
        return bottle.template(tpl,  data = data, other = other)

@bottle.route('/')
def firstpage ():
    data = None
    acc = accept (bottle.request)
    tpl = template ('firstpage')
    show_data = output_representation (data,  acc,  tpl)
    return show_data

@bottle.route('/searchresult')
def searchresult ():
    input = bottle.request.query.input
    acc = accept (bottle.request)
    tpl = template ('search')
    show_data = output_representation (input,  acc,  tpl)
    return show_data
    
    

 
if __name__=="__main__":
    if len (sys.argv) > 1:
        prefix = sys.argv [1]

        database_obj = biv.Database (prefix)
        db = biv.Database(prefix)
        tpl_dir = os.path.join (prefix, 'tpl')
        bottle.debug(True)
        bottle.run (host='localhost',  port = 8080)
    else:
        print "Usage %s <prefix>" % sys.argv [0]
        sys.exit (-1)
else:
    path = os.path.dirname(os.path.realpath(__file__))
    prefix = os.path.dirname(path)
    tpl_dir = os.path.join = (prefix, 'tpl')

    env_obj = biv.Environment (prefix)

    
    application = bottle.default_app()
