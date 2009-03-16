#/bin/sh

TARGETDIR=html

for f in `ls -1 *.txt`; do
    rst2html.py $f ${TARGETDIR}/${f%.txt}.html;
done
