
"""
.. module:: llvmutils
   :platform: Unix, Windows
   :synopsis: Offers tools to use the llvm infrastructure 9.0.0

.. moduleauthor:: Juan Carlos de la Torre <juan.detorre@uca.es>

"""


import os
import subprocess
import time
from shutil import copy as copyfile
import sys
import numpy as np

class LlvmUtils():
    '''
    llvmpath = llvm path
    basepath = work path
    bechmark = benchmark folder name, has to be in work path
    generator = script to merge all benchmark suite
    source = name for benchmark IR code
    runs = how many times should the benchmark be run
    jobid = job identifier code
    '''

    def __init__(self, llvmpath: str="/llvm/bin/", clangexe: str="clang", optexe: str="opt", 
                llcexe: str="llc", basepath: str="./", benchmark: str = "polybench_small",
                source: str="polybench_small_original.bc", runs: int=1, jobid: str=""):
        self.llvmpath = llvmpath
        self.clangexe = clangexe
        self.optexe = optexe
        self.llcexe = llcexe
        self.basepath = basepath
        self.benchmark = benchmark
        self.source = source
        self.runs = runs
        self.jobid = jobid
        self.onebyones = 0

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

    def get_conditional_jumps(self) -> int:
        result = 0
        with open("{}optimized_{}.ll".format(self.basepath,self.jobid),'r') as file:
            for line in file.readlines():
                result += line.count("jl")
                result += line.count("jge")
        return result

    def get_jmp(self) -> int:
        result = 0
        with open("{}optimized_{}.ll".format(self.basepath,self.jobid),'r') as file:
            for line in file.readlines():
                result += line.count("jmp")
        return result

    # To get the runtime
    def get_runtime(self) -> float:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        average = 0.0
        for _ in range(self.runs):
            start_time = time.time()
            os.system("{}exec_{}.o".format(self.basepath,self.jobid))
            average += time.time() - start_time
        average /= self.runs
        return average

    # To get the number of lines of code
    def get_codelines(self) -> int:
        result = 0
        with open("{}optimized_{}.ll".format(self.basepath,self.jobid),'r') as file:
            result = len(file.readlines())
        return result

    # original.bc --> optimized.bc
    def toIR(self, passes: str = '-O3') -> bool:
        source = "{}optimized_{}.bc".format(self.basepath,self.jobid)
        output = source
        if (os.path.exists(source)):
            os.remove(source)
        copyfile("{}{}".format(self.basepath,self.source), source)
        resultcode = self.opt(source, output, passes)
        
        if resultcode: raise Exception(f"opt failed ({resultcode}): {passes}")

    # optimized.bc --> optimized.o
    def toExecutable(self): 
        source = "{}optimized_{}.bc".format(self.basepath, self.jobid)
        output = "{}exec_{}.o".format(self.basepath, self.jobid)
        resultcode = self.clang(source, output)

        if resultcode: raise Exception(f"clang failed ({resultcode}):\n\tsource: '{source}'\n\toutput: '{output}'")

    # optimized.bc --> optimized.ll
    def toAssembly(self, source: str = "optimized.bc", output: str = "optimized.ll"):
        source = "{}{}".format(self.basepath,source.replace(".bc","_{}.bc".format(self.jobid)))
        output = "{}{}".format(self.basepath,output.replace(".ll","_{}.ll".format(self.jobid)))
        resultcode = self.llc(source, output)

        if resultcode: raise Exception(f"llc failed ({resultcode}):\n\tsource: '{source}'\n\toutput: '{output}'")

    # To apply transformations in one line
    def opt(self, source: str, output: str, passes: str) -> bool:
        completed = subprocess.run("{}{} {} {}optimized_{}.bc -o {}optimized_{}.bc".format(
            self.llvmpath,self.optexe,passes,self.basepath,self.jobid,self.basepath,
            self.jobid),shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return completed.returncode

    def llc(self, source: str, output: str):
        completed = subprocess.run("{}{} {}{} -o {}{}"\
            .format(self.llvmpath,self.llcexe, self.basepath,source,self.basepath,output), 
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return completed.returncode

    def clang(self, source: str, output: str):
        completed = subprocess.run("{}{} -lm -O0 -Wno-everything -disable-llvm-optzns -disable-llvm-passes -Xclang -disable-O0-optnone {} -o {}"\
            .format(self.llvmpath, self.clangexe, source, output),
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
                    