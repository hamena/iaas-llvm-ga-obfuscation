
"""
.. module:: LlvmUtils
   :platform: Unix, Windows
   :synopsis: Offers tools to use the llvm infrastructure 9.0.0

.. moduleauthor:: Juan Carlos de la Torre <juan.detorre@uca.es>, Jose Crespo Guerrero <jose.crespoguerrero@uca.es>

"""

import subprocess
from shutil import copy as copyfile
import sys
import numpy as np

class LlvmUtils():
    '''
    llvmpath: llvm path
    basepath: work path
    generator: script to merge all benchmark suite
    '''
    def __init__(self, llvmpath: str="/llvm/bin/", clangexe: str="clang", optexe: str="opt", 
                llcexe: str="llc"):
        self.llvmpath = llvmpath
        self.clangexe = clangexe
        self.optexe = optexe
        self.llcexe = llcexe

    @staticmethod
    def get_passes() -> list:
        all_passes = ["-tti","-tbaa","-scoped-noalias","-assumption-cache-tracker","-targetlibinfo","-verify",
                      "-ee-instrument","-simplifycfg","-domtree","-sroa","-early-cse","-lower-expect",
                      "-profile-summary-info","-forceattrs","-inferattrs","-callsite-splitting","-ipsccp",
                      "-called-value-propagation","-attributor","-globalopt","-mem2reg","-deadargelim",
                      "-basicaa","-aa","-loops","-lazy-branch-prob","-lazy-block-freq","-opt-remark-emitter",
                      "-instcombine","-basiccg","-globals-aa","-prune-eh","-inline","-functionattrs",
                      "-argpromotion","-memoryssa","-early-cse-memssa","-speculative-execution","-lazy-value-info",
                      "-jump-threading","-correlated-propagation","-aggressive-instcombine","-libcalls-shrinkwrap",
                      "-branch-prob","-block-freq","-pgo-memop-opt","-tailcallelim","-reassociate",
                      "-loop-simplify","-lcssa-verification","-lcssa","-scalar-evolution","-loop-rotate","-licm",
                      "-loop-unswitch","-indvars","-loop-idiom","-loop-deletion","-loop-unroll","-mldst-motion",
                      "-phi-values","-memdep","-gvn","-memcpyopt","-sccp","-demanded-bits","-bdce","-dse",
                      "-postdomtree","-adce","-barrier","-elim-avail-extern","-rpo-functionattrs","-globaldce",
                      "-float2int","-loop-accesses","-loop-distribute","-loop-vectorize","-loop-load-elim",
                      "-slp-vectorizer","-transform-warning","-alignment-from-assumptions","-strip-dead-prototypes",
                      "-constmerge","-loop-sink","-instsimplify","-div-rem-pairs"]
        return all_passes

    # original.bc --> optimized.bc
    def toIR(self, source: str, output: str, passes: str = '-O3') -> bool:
        resultcode = self.opt(source, output, passes)
        if resultcode: raise Exception(f"opt failed ({resultcode}): {passes}")

    # optimized.bc --> optimized.o
    def toExecutable(self, source: str, output: str): 
        resultcode = self.clang(source, output)
        if resultcode: raise Exception(f"clang failed ({resultcode}):\n\tsource: '{source}'\n\toutput: '{output}'")

    # optimized.bc --> optimized.ll
    def toAssembly(self, source: str, output: str):
        resultcode = self.llc(source, output)
        if resultcode: raise Exception(f"llc failed ({resultcode}):\n\tsource: '{source}'\n\toutput: '{output}'")

    def opt(self, source: str, output: str, passes: str) -> bool:
        command = "{}{} {} {} -o {}".format(self.llvmpath, self.optexe, passes, source, output)
        completed = subprocess.run(command,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return completed.returncode

    def llc(self, source: str, output: str):
        command = "{}{} {} -o {}".format(self.llvmpath, self.llcexe, source, output)
        completed = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return completed.returncode

    def clang(self, source: str, output: str):
        command = "{}{} -lm -O0 -Wno-everything -disable-llvm-optzns -disable-llvm-passes -Xclang -disable-O0-optnone {} -o {}"\
            .format(self.llvmpath, self.clangexe, source, output)
        completed = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return completed.returncode

    # To add a file to the output file
    @staticmethod
    def mergeDict(input_: str,output_: str):
        dic = dict()
        LlvmUtils.fileToDictionary(input_,dic)
        LlvmUtils.fileToDictionary(output_,dic)
        LlvmUtils.dictionaryToFile(output_,dic)

    # File to dictionary
    @staticmethod
    def fileToDictionary(input_: str, dic: list):
        with open(input_,"r") as file:
            lines = file.readlines()
            for line in lines:
                index = line.rfind(',')
                key = "["+"{}".format(line[:index])+"]"
                value = "{}".format(line[index+1:])[:-1]
                dic.update({key: value})

    # Dictionary to file
    @staticmethod
    def dictionaryToFile(filename: str, dic: list):
        with open(filename,"w") as file:
            for keys,values in dic.items():
                key = '{}'.format(keys).replace("[","").replace("]","")
                key = '{}'.format(key).replace(", ",",")
                file.write('{},{}\n'.format(key,values))

    # To encode file from passes to integers
    @staticmethod
    def encode(input_: str, output_: str):
        with open(input_,'r') as inputfile:
            lines = inputfile.readlines()
            with open(output_,'w') as ouputfile:
                for line in lines:
                    index = line.rfind(',')
                    keys = "{}".format(line[:index]).split(",")
                    value = "{}".format(line[index+1:])[:-1]
                    newkey = ""
                    for key in keys:
                        newkey += '{},'.format(LlvmUtils.get_passes().index(key))
                    ouputfile.write('{}{}\n'.format(newkey,value))

    # To decode file from integers to passes
    @staticmethod
    def decode(input_: str,output_: str):
        with open(input_,'r') as inputfile:
            lines = inputfile.readlines()
            with open(output_,'w') as ouputfile:
                for line in lines:
                    index = line.rfind(',')
                    keys = "{}".format(line[:index]).split(",")
                    value = "{}".format(line[index+1:])[:-1]
                    newkey = ""
                    for key in keys:
                        newkey += '{},'.format(LlvmUtils.get_passes()[int(key)])
                    ouputfile.write('{}{}\n'.format(newkey,value))
                


class LlvmFiles():
    '''
    basepath = working directory
    source_bc = path to a llvm bc source file
    jobid: files namespace
    '''
    def __init__(self, basepath: str='./', source_bc: str='polybench_small_original.bc', jobid: str=''):
        self.basepath = basepath
        self.jobid = jobid
        self.original_bc = f"{basepath}{source_bc}"
        self.optimized_bc = f"{basepath}{jobid}_optimized.bc"
        self.optimized_ll = f"{basepath}{jobid}_optimized.ll"
        self.optimized_exe = f"{basepath}{jobid}_optimized.o"

    def get_basepath(self):
        return self.basepath
    
    def get_jobid(self):
        return self.jobid
    
    def get_original_bc(self):
        return self.original_bc
    
    def get_optimized_bc(self):
        return self.optimized_bc
    
    def get_optimized_ll(self):
        return self.optimized_ll
    
    def get_optimized_exe(self):
        return self.optimized_exe