#!/bin/bash
aria2c -c 5 -x 10 -d $OUTDIR -i $IMAGE_URLS_FILE
