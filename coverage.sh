#!/bin/sh

coverage run --branch --source=lint8 ./test.py
coverage html
