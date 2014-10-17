#!/usr/bin/python
#-*- coding:  utf8 -*-

import argparse
import biv
import xapian

def search (db_xap_path, querystring, offset, pagesize):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve

    # Open the database we're going to search.
    db = xapian.Database (db_xap_path)

    # Set up a QueryParser with a stemmer and suitable prefixes
    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("swedish"))
    queryparser.set_stemming_strategy(queryparser.STEM_SOME)
    queryparser.add_prefix("frequency", "XF")
    queryparser.add_prefix("system", "XS")

    # And parse the query
    query = queryparser.parse_query (querystring)

    # Use an Enquire object on the database to run the query
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    # And print out something about each match
    matches = []
    for match in enquire.get_mset(offset, pagesize):
        fields = match.document.get_data()
        print u"%(rank)i: #%(docid)3.3i %(data)s" % {
            'rank': match.rank + 1,
            'docid': match.docid,
            'data': fields
            }
        matches.append(match.docid)

    # Finally, make sure we log the query and displayed results
    #support.log_matches(querystring, offset, pagesize, matches)
















#-----------------------------------------------------------------------------------------------------------
if __name__=='__main__':#gör att det bara körs om det är huvudprogrammet

    parser = argparse.ArgumentParser('Search in the undesired effects') 

    parser.add_argument('-p' ,'--prefix',  help = 'The path to database')
    parser.add_argument('-s' ,'--search',  help = 'Search string')
    parser.add_argument('-o' ,'--offset',  help = 'Set offset, defines starting point within result set')
    parser.add_argument('-a' ,'--pagesize',  help = 'Set pagesize, defines number of records to retrieve')
    parser.add_argument ('command',  help="Valid actions: search")


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
        
    if args.command =='search':
        if not args.search:
            import sys
            parser.error ('If you want to search you have to specify a string for the search') 
            sys.exit (-1)
        else:
            if args.offset:
                assert args.offset.isdigit ()
                offset = int (args.offset) or 0
            if args.pagesize:
                assert args.pagesize.isdigit ()
                pagesize = int (args.pagesize) or 10
            search (db_xap_path,  args.search,  offset, pagesize)
else:
    pass





