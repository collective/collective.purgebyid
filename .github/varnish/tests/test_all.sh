#!/bin/bash
for f in /tests/*vtc; do
    varnishtest $f
done