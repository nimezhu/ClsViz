# ClsViz

ClsViz is designed to be a browser for table type data. It combines the advantage of various technology such as spectral clustering, model selection, neighborhood embedding and javascript interactive figure to help investigators to get a quick data impression.  

## Features
### Clustering
- Spectral Clustering ( Coordinate Translate Based on Similarity Matrix)
- Integrated Multiple Sources Data
- Automatically select cluster number k
- tSNE for Visualizaiton

### Visualization

#### Install from Go get
go get -u github.com/nimezhu/ClsViz/viz

viz demo.cls.tsv

#### Download from Binary
[Download Binary](http://genome.compbio.cs.cmu.edu/~xiaopenz/clsviz/viz/)

#### Obsoleted Python version
[Python Version](https://github.com/nimezhu/ClsViz/tree/Python)

## Dependency
### Clustering Program Dependency
- scipy
- numpy
- scikit-learn
- argparse
- csv

