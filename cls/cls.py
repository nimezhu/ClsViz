#!/usr/bin/env python
# Programmer : zhuxp
# Date: 
# Last-modified: 07-29-2015, 13:42:12 EDT
from __future__ import print_function
VERSION="0.6"
import os,sys,argparse
import numpy as np
from numpy import linalg as LA
from scipy.linalg import eigh
import numpy as np
import itertools
from scipy.cluster.vq import kmeans,vq
from numpy import exp,min,arccos,sin,trace,compress,equal,array,sqrt,isnan,power,mean,cos,median
from scipy.spatial.distance import squareform,pdist,euclidean
from sklearn.metrics import pairwise_distances
from os.path import splitext,basename
import logging
from sklearn.manifold import TSNE
import random
import csv
#TODO
#v5: 1.add combine tables (DONE)
#    2.add euclidean distance (DONE)
#    3.add mean, min to data fusion function (DONE, to test)
#v6:
#    - fix k=1 bug
#v7:
#    - add choose k method ( randomized matrix and choose eigencutoff, or proportion(old one) or , or eigenvalue cutoff or eigenvalue drop)
#v8
#    5.improve euclidean distance guessing the sigma 
#    6.add naive k-means to compare (after determine k ? impulse normalization ? option for m?) write another simple program?
#    7.add kernel k-means options.? write another program.
#    8.add Report output. (google sheet readme? sheet2? Mutual information gain)
def ParseArg():
    ''' This Function Parse the Argument '''
    p=argparse.ArgumentParser( description = 'Example: %(prog)s -h', epilog='Library dependency : scipy scikit-learn numpy argparse csv')
    p.add_argument('-v','--version',action='version',version='%(prog)s '+VERSION)
    p.add_argument('-i','--input',dest="input",nargs="*",help="input expression matrix files")
    p.add_argument('-o','--output',dest="output",type=str,default="stdout",help="output file DEFAULT: STDOUT")
    p.add_argument('-c',dest="start_col",type=int,default=2,help="start column default:%(default)i")
    p.add_argument('-e','--eigen_cutoff',dest="e",type=float,default=0.95,help="eigen proportion [K=2] , or eigen cutoff [K=4]")
    p.add_argument('-K','--choose_k_method',dest="K",type=int,default=2, choices=[1,2,3,4] ,help="choose k method. 1. compare with eigenvalue of permutation matrix , 2. eigen proportion, 3. choose k number, 4. eigenvalue threshold")
    p.add_argument('-k','--k_groups',dest="k",type=int,default=4, help="choose k number.")
    p.add_argument('-m','--metric',dest="m",type=int,choices=[0,1,2],default=0,help="metric method 0.correlation coefficient 1.cosine 2.euclidean (radius basis function)")
    p.add_argument('-H','--header',dest="h",type=int,default=1,help="header rows number")
    p.add_argument('-N','--name_col',dest="n",type=int,default=1,help="name col number")
    p.add_argument('-T','--transpose',dest="T",action="store_true",default=False,help="cluster columns")
    p.add_argument('-M','--merge_table',dest="M",action="store_true",default=False,help="merging table into big table")
    p.add_argument('-F','--fusion_method',dest="F",type=int,choices=[0,1,2],default=0, help="data fusion method: 0.geometry_mean, 1.min , 2.mean")
    if len(sys.argv)==1:
        print(p.print_help(),file=sys.stderr)
        exit(0)
    return p.parse_args()
def gini_index(iterator):
    '''
    Gini coefficient
    reference:
        http://en.wikipedia.org/wiki/Gini_coefficient
    '''
    l=[i for i in iterator]
    l.sort()
    s1=0.0
    s2=0.0
    y=[]
    n=len(l)
    for i,x in enumerate(l):
        s1+=(i+1)*x
        s2+=x
    if s2==0: return 0.0
    G=2*s1/(n*s2)-float(n+1)/n
    return G
def Main():
    global args,out,logger
    logger=logging.getLogger("akmeans logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    args=ParseArg()
    out=fopen(args.output,"w")
    #fname,ext=splitext(args.input)
    mlist=[]
    namelist=[]
    slist=[]
    idxlist=[]
    colnamelist=[]
    for f in args.input:
        logger.info("reading "+f)
        colnames,names,mat=read_matfile(f,args.h,args.start_col-1,args.n-1,args.T)
        mlist.append(mat)
        namelist.append(names)
        colnamelist.append(colnames)
        slist.append(mat_to_smat(mat,args.m))
        idx,_=akmeans(slist[-1],args.K,args.e)
        lst=idx_to_list(idx)
        lst.sort(key=lambda x: average_rank_score([mat[i] for i in x]),reverse=True)
        for i,l in enumerate(lst):
            for j in l:
                idx[j]=i
        idxlist.append(idx)
    for i in idxlist:
        logger.info(i)
    if args.F==0:
        S=geometry_mean(slist)
    elif args.F==1:
        S=mat_min(slist)
    elif args.F==2:
        S=mat_mean(slist)
    idx,vectorY=akmeans(S,args.K,args.e)
    lst=idx_to_list(idx)
    lst.sort(key=lambda x: list_average_rank_score([[mat[i] for i in x] for mat in mlist]),reverse=True)
    for i,l in enumerate(lst):
        for j in l:
            idx[j]=i
    idxlist.append(idx)
    logger.info(idx)
    idxt=array(idxlist).T 
    model=TSNE(n_components=2)
    tsneY=model.fit_transform(vectorY)
    if args.M:
        print("gene\ttSNE_x\ttSNE_y\t"+"\t".join([basename(j0) for j0 in args.input])+"\t"+"Interagrated",file=out,end="")
        for i in colnamelist:
            print("\t"+"\t".join(i),end="",file=out)
        print("",file=out)
        for i,xs in enumerate(itertools.izip(tsneY,idxt)):
            x=xs[1]
            tx,ty=xs[0]
            print(names[i]+"\t"+str(tx)+"\t"+str(ty)+"\t"+"\t".join([str(j) for j in x]),file=out,end="");
            for j,m in enumerate(mlist):
                print("\t"+"\t".join(str(k) for k in m[i]),file=out,end="")
            print("",file=out)
    else:
        print("gene\ttSNE_x\ttSNE_y\t"+"\t".join([basename(j0) for j0 in args.input])+"\t"+"Interagrated",file=out)
        for i,xs in enumerate(itertools.izip(tsneY,idxt)):
            x=xs[1]
            tx,ty=xs[0]
            print(names[i]+"\t"+str(tx)+"\t"+str(ty)+"\t"+"\t".join([str(j) for j in x]),file=out);

def mat_min(slist):
    s=slist[0]
    for m in slist:
        s=np.minimum(s,m)
    return s

def read_matfile(f,header=1,col=1,name_col=0,transpose=False):  #start col 0
    fin=fopen(f,"r")
    headers=[]
    mat=[]
    names=[]
    iter=parse(fin)
    for i in xrange(header):
        headers.append(iter.next());
    for i in iter:
        names.append(i[name_col]);
        mat.append([float(a) for a in i[col:]])
    if len(headers)==0:
        headers.append([str(f)+".V"+str(j+1) for j in xrange(len(mat[0]))]);
    if transpose:
        mat=np.array(mat)
        tmat=mat.T
        return names,headers[-1][col:],tmat
    else:
        return headers[-1][col:],names,np.array(mat)
def mat_to_smat(mat,method=0):
    if method==0:
        S=exp(-(sin((arccos(np.corrcoef(mat))/2)**2)))
    elif method==1:
        S=pairwise_distances(mat, metric="cosine")
        S[isnan(S)]=1.0
        S=1.01-S
    elif method==2:  #euclidean distance + Radius Basis Function
        S=pairwise_distances(mat, metric="euclidean")
        sigma=min([median(S),mean(S)]); # guessingt the sigma
        #sigma=mean(S)
        sigma2=sigma*sigma;
        for i,row in enumerate(S):
            for j,x in enumerate(row):
                S[i][j]=exp(-S[i][j]*S[i][j]/2/sigma2)
    S[isnan(S)]=0.01
    #TODO  other method
    return S
def geometry_mean(Slist):
    l=len(Slist)
    S=power(Slist[0],1.0/l)
    for S0 in Slist[1:]:
        S*=power(S0,1.0/l)
    return S
def mat_mean(Slist):
    l=len(Slist)
    S=Slist[0]
    for S0 in Slist[1:]:
        S+=S0
    S=S/l
    return S

def idx_to_list(idx):
    m=0
    for i in idx:
        if m<i: m=i
    l=[[] for i in xrange(m+1)]
    for i,x in enumerate(idx):
        l[x].append(i)
    return l
def list_average_rank_score(x):
    s=[average_rank_score(i) for i in x]
    return mean(s)
def time_index(x):
    return 1.0-rank_score(x)
def average_rank_score(x):
    l=len(x)
    s=0.0
    for i in x:
        s+=rank_score(i)
    return s/l
def rank_score(x):
    s=sum(x)
    if s==0:
        s=1
    a=[float(j)/s for j in x]
    l=len(x)
    s1=0.0
    s2=0.0
    for i in a:
        s1+=i
        s2+=s1*1.0/l
    return s2
def permutation(S1):
    S=np.copy(S1)
    l=len(S)
    for i,x in enumerate(S):
        newx  = np.random.permutation(x[i+1:l])
        for j,y in enumerate(newx):
            S[i][j+1+i]=newx[j]
            S[j+1+i][i]=newx[j]
    return S
def random_mat(S1):
    S=np.copy(S1)
    l=len(S)
    for i,x in enumerate(S):
        for j in xrange(l-i-1):
            rnd=random.random()
            S[i][j+1+i]=rnd
            S[j+1+i][i]=rnd
    return S


def akmeans(S,kmethod,ro):
    D=sum(S)
    l=len(S)
    print("D=",D)
    D1=D**-1
    c=D1*S
    tr=trace(c)
    if l<50:
        value,vector=eigh(c,eigvals=(0,l-1))
    else:
        value,vector=eigh(c,eigvals=(l-50,l-1))
    #vector=_norm_vector(vector)
    if kmethod==1:
        PS=permutation(S)
        #PS=random_mat(S)
        PD=sum(PS)
        PD1=PD**-1
        Pc=PD1*S
        Ptr=trace(Pc)
        if l<50:
            Pvalue,Pvector=eigh(Pc,eigvals=(0,l-1))
        else:
            Pvalue,Pvector=eigh(Pc,eigvals=(l-50,l-1))
        print("random eigen value =", Pvalue)
        diff=[i-j for i,j in itertools.izip(value,Pvalue)]
        print("diff =",diff)
    rank=range(0,l)
    print("value=",value) 
    max_value=value[-1]
    k=0
    s=0
    if kmethod==2:
        for i in value[::-1]:
            s+=i
            if float(s)/tr<ro:
                k+=1
            else:
                break
        k+=1
    elif kmethod==1:
        k=1
        i0=True;
        eigen_change_cutoff=0.001
        for i,j in itertools.izip(value[::-1],Pvalue[::-1]):
                if i0:
                    i0=False
                    continue
                if i<j+eigen_change_cutoff:
                    print(i,j)
                    break
                else:
                    k+=1
    elif kmethod==3:
        k=args.k
    elif kmethod==4:
        for i in value[::-1]:
            s=i
            if float(s)>ro:
                k+=1
            else:
                break

    print(vector[:,-k-1:-1])
    if k==1:
        print("N=1")
        return [0 for i in range(l)],vector[:,-2:-1]
    DBI=10000;
    idx=None;
    centroids=None;
    k_iter_times=5;
    if k>10:
        k_iter_times=2;
    for i in range(k_iter_times):
        n_centroids,_ = kmeans(vector[:,-k-1:-1],k)
        n_idx,_=vq(vector[:,-k-1:-1],n_centroids)
        n_DBI=dbi(n_centroids,n_idx,vector[:,-k-1:-1])
        if n_DBI<DBI:
            DBI=n_DBI
            centroids=n_centroids
            idx=n_idx
            print("DBI=",dbi(centroids,idx,vector[:,-k-1:-1]))
    print("N=",len(centroids))
    return idx,vector[:,-k-1:-1]
       
def rep(x):
    s=sum([float(i) for i in x])
    return [round(j/s,2) for j in x]    
 
def dbi(mu,idx,obs):
    d=dist(mu,idx,obs)
    return davies_bouldin_index(mu,d)
def dist(mu,idx,obs):
    MIN_DIST=0.01
    dist=[0.0 for i in xrange(mu.shape[0])]
    for i in xrange(mu.shape[0]):
        j=-1
        a=compress(equal(idx,i),obs,0)
        for d0 in a:
            dist[i]+=np.sum((d0-mu[i])**2)
            j+=1
        if j>-1:
            dist[i]/=(j+1)
        else:
            dist[i]=MIN_DIST
    return dist
def davies_bouldin_index(mu,dist):
    db=0.0
    n=len(mu)
    for i in xrange(n):
        db+=max(array([(sqrt(dist[j])+sqrt(dist[i]))/euclidean(mu[i],mu[j]) for j in xrange(n) if j!=i]))
    db*=1.0/n
    return db
    db=0.0
    n=len(mu)
    for i in xrange(n):
        db+=max(array([(sqrt(dist[j])+sqrt(dist[i]))/euclidean(mu[i],mu[j]) for j in xrange(n) if j!=i]))
    db*=1.0/n
    return db

def open_output(output):
    out=None
    if output=="stdout":
        out=sys.stdout
    else:
        try:
            if os.path.isfile(output):
                i=1;
                newname=None
                while(True):
                    name,ext=os.path.splitext(output)
                    newname=name+"("+str(i)+")"+ext
                    if not os.path.isfile(newname):
                        break
                    i+=1
                output=newname
                logging.warn("output file exists, automatically rename the output file to "+output)
            out=open(output,"w")
        except IOError:
            print("can't open file ",output,"to write. Using stdout instead",file=sys.stderr)
            out=sys.stdout
    return out

def open_input(input):
    fin=None
    if input=="stdin":
        fin=sys.stdin
    else:
        try:
            x=input.split(".")
            if x[-1]=="gz":
                fin=gzip.open(input,"r")
            else:
                fin=open(input,"r")
        except IOError:
            print("can't read file",input,file=sys.stderr)
            fin=sys.stdin
    return fin
    
def fopen(file,mode="r",**kwargs):
    '''
    '''
    if mode=="w":
        return open_output(file)
    if mode=="r":
        return open_input(file)
    return None
def parse(handle,**dict):
    sep="\t"
    if dict.has_key("sep"):
        sep=dict["sep"]
    if isinstance(handle,str):
        try:
            handle=fopen(handle,"r")
            for i in csv.reader(handle,delimiter=sep):
                if len(i)==0:continue
                if i[0].strip()[0]=="#": continue
                yield tuple(i)
            handle.close()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror),file=sys.stderr)
    else:
        try:    
            for i in csv.reader(handle,delimiter=sep):
                if len(i)==0: continue
                if i[0].strip()[0]=="#": continue
                yield tuple(i)
        except:
            raise    
    
if __name__=="__main__":
    Main()
 
 
 
 
