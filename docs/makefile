.PHONY: default all html tex dvi pdf clean clean_tex distclean

DOCNAME      = mpi4py

SOURCE_HTML  = ${DOCNAME}-html.rst
SOURCE_LATEX = ${DOCNAME}-latex.rst
SOURCES_TXT  = titlepage.txt \
               intro.txt  \
               mpi.txt \
               download.txt \
               install.txt \
               tutorial.txt \
               references.txt \
               links.txt


RST2HTML  = rst2html
RST2LATEX = rst2latex

LATEX     = latex -interaction=batchmode
PDFLATEX  = pdflatex -interaction=batchmode


default: html

all: html dvi pdf

html: ${DOCNAME}.html

tex: ${DOCNAME}.tex

dvi:  ${DOCNAME}.dvi

pdf:  ${DOCNAME}.pdf


${DOCNAME}.html: ${SOURCE_HTML} ${SOURCES_TXT}
	${RST2HTML} $< $@

${DOCNAME}.tex: ${SOURCE_LATEX} ${SOURCES_TXT}
	${RST2LATEX} $< $@

${DOCNAME}.dvi: ${DOCNAME}.tex
	${LATEX} $<

${DOCNAME}.pdf: ${DOCNAME}.tex ${DOCNAME}.dvi
	${PDFLATEX} $<


clean: clean_tex
	${RM} ${DOCNAME}.html ${DOCNAME}.tex ${DOCNAME}.dvi ${DOCNAME}.pdf

clean_tex: 
	${RM} *.aux *.log *.out *.toc *.ind *.ilg

distclean: clean
	${RM} *~
