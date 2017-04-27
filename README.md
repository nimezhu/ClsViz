# ClsViz

ClsViz is designed to be a browser for table type data. It combines the advantage of various technology such as spectral clustering, model selection, neighborhood embedding and javascript interactive figure to help investigators to get a quick data impression. Its features are summarized into the followings.
- Spectral Clustering ( Coordinate Translate Based on Similarity Matrix)
- Integrated Multiple Sources Data
- Automatically select cluster number k
- tSNE for Visualizaiton

## Install
ClsViz is implemented in python(for clustering) and GO (for visualization). It can be installed in most OSX, windows, linux machines or any OS with a web browser. The install is easy for most people. But it can be a bit of headache if the corresponding environment is not yet set up.

###### Python environment for Cls
The following python packages are required by ClsViz, which can be installed by [pip](https://pip.pypa.io/en/stable/installing/).
```
scipy
numpy
scikit-learn
argparse
csv
```

###### GO binaries for Viz
The pre-compiled GO binaries for mac, linux and windows OS can be downloaded from this [link](http://genome.compbio.cs.cmu.edu/~xiaopenz/clsviz/viz/). Please note that there're binaries (32 bit or 64 bit) for two type of windows machines. A quick way to tell which binaries to download is to check the memory size of your machine. The 32 bit windows OS can not support more than 4Gb of RAM/memory.

###### install Viz from GitHub
If the binaries does not work on your machine, you can also get the source and binary files from this site via GO. (You have to get GO environment installed beforehead. To get GO installed, you can refer to [this link](https://golang.org/doc/install)).

`go get -u github.com/nimezhu/ClsViz/viz`

###### Test installation
To test your ClsViz installation, find the demo file *demo.cls.tsv* and run the following command from your terminal.

`viz demo.cls.tsv`

You should have viz automatically set up in your PATH if you installed from GO get command. If you download the pre-compiled binaries, please make sure they are in PATH with correct permissions.
