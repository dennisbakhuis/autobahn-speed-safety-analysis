MAIN = main
FIGURES = ../output/figures

.PHONY: all clean figures

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	pdflatex $(MAIN)
	bibtex $(MAIN)
	pdflatex $(MAIN)
	pdflatex $(MAIN)

figures:
	cd .. && .venv/bin/python scripts/create_figures.py

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.synctex.gz $(MAIN).pdf
