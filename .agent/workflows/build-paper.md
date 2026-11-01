# Workflow: Build Paper

## Description
Generates high-resolution figures from pipeline metrics, updates LaTeX/Markdown tables, and compiles the IEEE research paper to PDF.

## Execution
```powershell
python -m parcl_core.paper_gen
pandoc paper/paper.md -o paper/paper.pdf --citeproc --pdf-engine=xelatex
```
