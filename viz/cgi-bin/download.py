#!/usr/bin/env python
import cgi, cgitb
import tempfile
import os,sys
form = cgi.FieldStorage()
output_format=form.getvalue('output_format');
data=form.getvalue('data')
height=form.getvalue('height')
width=form.getvalue('width')
fn = form.getvalue('filename');
if (output_format=="svg"):
    print "Content-Disposition:attachment; filename=\"{fn}.svg\"".format(fn=fn);
    print "Content-type:img/svg+xml\r\n\r\n"
    print "{}".format(data);
elif (output_format=="pdf" or output_format=="png"):
    input_file=tempfile.NamedTemporaryFile()
    output_file=tempfile.NamedTemporaryFile()
    input_file.write(data)
    input_file.flush()
    command="rsvg-convert -h {height} -w {width} -o {output_file} -f {output_format} {input_file}".format(output_file=output_file.name,input_file=input_file.name,output_format=output_format,height=height,width=width)
    os.system(command)

    if output_format=="pdf":
        print "Content-Disposition:attachment; filename=\"{fn}.pdf\"".format(fn=fn);
        print "Content-type:application/x-pdf\r\n\r\n"
        o=open(output_file.name,"rb")
        print o.read()
        o.close()
    if output_format=="png":
        sys.stdout.write("Content-Disposition:attachment; filename=\"{fn}.png\"\n\r".format(fn=fn))
        sys.stdout.write("Content-type:img/png\r\n\r\n")
        sys.stdout.write(file(output_file.name,"rb").read())
    input_file.close()
    output_file.close()
elif output_format=="json":
    print "Content-Disposition:attachment; filename=\"{fn}.json\"".format(fn=fn);
    print "Content-type:application/json\r\n\r\n"
    print "{}".format(data);
elif output_format=="html":
    print "Content-Disposition:attachment; filename=\"{fn}.html\"".format(fn=fn);
    print "Content-type:application/text\r\n\r\n"
    print "{}".format(data);
    
