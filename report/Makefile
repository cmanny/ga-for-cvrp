SHELL := /bin/bash

SOURCES = $(wildcard *.tex)
TARGETS = $(patsubst %.tex, %.pdf, ${SOURCES})

TEXMFLOCAL = "/home/crypto/texmf"

${TARGETS} : %.pdf : %.tex $(wildcard %.bib)
	@for i in `seq 3`                           ; do   \
           TEXMFLOCAL="${TEXMFLOCAL}" pdflatex ${*} ;      \
           if grep -q "bibliography" ${*}.tex       ; then \
             TEXMFLOCAL="${TEXMFLOCAL}" bibtex ${*} ;      \
           fi                                       ;      \
         done

all      : ${TARGETS}

clean    :
	@rm -f *.{aux,bbl,blg,loa,lof,log,lol,lot,nav,out,snm,toc}

spotless : clean
	@rm -f ${TARGETS}

.DEFAULT_GOAL := all
