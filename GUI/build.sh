#!/bin/sh
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -Bbuild
cmake --build build

echo '\nBuild Finished.\nTo run, just run: build/TGUI'
