readcue
=======

Reads cue files and their FLAC albums and converts them to ALAC.

This started out as a simple project to extract the timings for each song in a large FLAC album and use ffmpeg to split the individual songs and convert them to ALAC. I thought it would be a lot smaller, but I was wrong, clearly.

Usage: readcue --alac [y|n] <cuefile>

Note: I use ALAC because that's the only way I can get lossless audio
on my iPod.

