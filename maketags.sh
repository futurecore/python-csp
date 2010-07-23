#!/bin/sh

find . -name *.py -print -or -name *.html -print | xargs etags
