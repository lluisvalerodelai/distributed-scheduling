#!/bin/zsh

fallocate -l 256M io_file.bin

echo "File created: io_file.bin (6GB)"
ls -lh io_file.bin
