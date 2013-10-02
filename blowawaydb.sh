#!/bin/sh
# We run this in two seperate files, since web2py is being called the second
# time with the -M option, it will recreate the tables for us from the db model files
../../web2py.py --shell=rimi -M --run=applications/rimi/blowawaydb.py
../../web2py.py --shell=rimi -M --run=applications/rimi/insert_test_data.py
