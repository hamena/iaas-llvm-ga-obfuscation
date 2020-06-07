#!/bin/bash

# llvm Path
llvm_path=$1

# benchmark option
tam=small

rm *.bc
${llvm_path}clang-10 -c -O0 -Xclang -disable-O0-optnone -emit-llvm *.c
${llvm_path}llvm-link-10 *.bc -o polybench_${tam}.bc
mv polybench_${tam}.bc polybench_${tam}_original.bc.bak
rm *.bc
mv polybench_${tam}_original.bc.bak polybench_${tam}_original.bc
${llvm_path}opt-10 -O3 polybench_${tam}_original.bc -o polybench_${tam}_optimized.bc
${llvm_path}clang-10 -lm -O0 polybench_${tam}_optimized.bc -o polybench_${tam}_optimized.out
time ./polybench_${tam}_optimized.out
