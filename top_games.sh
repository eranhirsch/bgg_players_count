#!/bin/bash

# For sorted by num of owners (without expansions):
seq 1 $1 | xargs -I"{}" bash -c 'curl "https://boardgamegeek.com/search/boardgame/page/{}?sort=numvoters&advsearch=1&q=&nosubtypes%5B0%5D=boardgameexpansion&B1=Submit&sortdir=desc" | grep -o -e "/boardgame/[0-9][0-9]*" | uniq | cut -d/ -f3'

# Sorted by rank:
# seq 1 $1 | xargs -I"{}" bash -c 'curl "https://boardgamegeek.com/browse/boardgame/page/{}" | grep -o -e "/boardgame/[0-9][0-9]*" | uniq | cut -d/ -f3'
