#!/usr/bin/env python
# Programmer : zhuxp
# Date: 
# Last-modified: 05-18-2015, 13:23:53 EDT
from __future__ import print_function
VERSION="0.3"
import os,sys
import cgi, cgitb
import os,sys
import json
import csv
import numpy
import urllib2

'''
 mininum dependency
 upload tsv file 
 covert them to google sheet style json file
'''
def parse_simple(handle,**dict):
    sep="\t"
    if dict.has_key("sep"):
        sep=dict["sep"]
    if isinstance(handle,str):
        try:
            handle=open(handle,"r")
            for i in csv.reader(handle,delimiter=sep):
                if len(i)==0:continue
                if i[0].strip()[0]=="#": continue
                yield tuple(i)
            handle.close()
        except IOError as e:
            print >>sys.stderr,"I/O error({0}): {1}".format(e.errno, e.strerror)
    else:
        try:    
            for i in csv.reader(handle,delimiter=sep):
                if len(i)==0: continue
                if i[0].strip()[0]=="#": continue
                yield tuple(i)
        except:
            raise     
def Main():
    cgitb.enable()
    form = cgi.FieldStorage()
    url=form.getvalue("url")
    #url=form['url']
    #url="http://garberwiki.umassmed.edu:8000/data/Jul2015/MDDC_Ifnb.resp.cls.tsv"
    print("Content-type:text/javascript\r\n\r\n")
    iter = parse_simple(urllib2.urlopen(url.replace("http:/","http://")))
    header=iter.next()
    rows=[]
    cols=[]
    for i,x in enumerate(header):
        cols.append({"label":x})
        
    for i in iter:
        rows.append(gsheet_row(i))
    data={}
    data["table"]={}
    data["table"]["cols"]=cols
    data["table"]["rows"]=rows
    print(json.dumps(data))
def gsheet_row(x):
    h={"c":[]}
    for i in x:
        if isanum(i) and not numpy.isnan(float(i)):
            if i.isdigit():
                h["c"].append({"v":int(i),"f":i})
            else:
                h["c"].append({"v":float(i),"f":i})
        else:
            h["c"].append({"v":i})
    return h

def isanum(str):
    try:
        float(str);
        return True;
    except ValueError:
        return False;

if __name__=="__main__":
    Main()


