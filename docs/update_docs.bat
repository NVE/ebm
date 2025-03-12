@echo off
call make clean
call sphinx-apidoc -f -e --no-toc -o ./source/modules/ ../ebm/
call make html
call start build\html\user_guide.html