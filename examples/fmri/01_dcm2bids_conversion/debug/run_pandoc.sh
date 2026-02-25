#!/bin/bash

for f in `ls *.html`; do
    pandoc $f --self-contained -o $f"_SELF.html"
done
