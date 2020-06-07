
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
    useperf = True means use perf for runtime so perf has to be installed
    '''

    def __init__(self, llvmpath: str="/llvm/bin/", clangexe: str="clang", optexe: str="opt", 
                llcexe: str="llc", basepath: str="./", benchmark: str = "polybench_small",
                generator: str="original_merged_generator.sh", source: str="polybench_small_original.bc",
                runs: int=1, jobid: str="", useperf: bool=True):
        self.llvmpath = llvmpath
        self.clangexe = clangexe
        self.optexe = optexe
        self.llcexe = llcexe
        self.basepath = basepath
        self.benchmark = benchmark
        self.generator = generator
        self.source = source
        self.runs = runs
        self.jobid = jobid
        self.onebyones = 0
        self.useperf = useperf

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

    # To convert the original benchmark into LLVM IR
    def benchmark_link(self) -> None:
        os.chdir("{}{}/".format(self.basepath,self.benchmark))
        os.system("./{} {}".format(self.generator,self.llvmpath))
        copyfile("{}".format(self.source),"../{}".format(self.source))
        os.chdir("../")

    # To get the runtime
    def get_runtime(self,passes: str = "-O3") -> float:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        average = 0.0
        if self.toIR(passes):
            os.system("{}{} -lm -O0 -Wno-everything -disable-llvm-optzns -disable-llvm-passes {}".format(
                       self.llvmpath,self.clangexe,"-Xclang -disable-O0-optnone {}optimized_{}.bc -o {}exec_{}.o".format(
                       self.basepath,self.jobid,self.basepath,self.jobid)))
            if self.useperf:
                cmd = subprocess.check_output("{}runtimes.sh {}exec_{}.o {}".format(
                          self.basepath,self.basepath,self.jobid,self.runs),shell=True)
                runtimes = np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)
                average = np.median(runtimes)
            else:
                for _ in range(self.runs):
                    start_time = time.time()
                    os.system("{}exec_{}.o".format(self.basepath,self.jobid))
                    average += time.time() - start_time
                average /= self.runs
        else:
            average = sys.maxsize
        return average

    # To get the number of lines of code
    def get_codelines(self,passes: str = '-O3',source: str = "optimized.bc",
                  output: str = "optimized.ll") -> int:
        source = "{}{}".format(self.basepath,source.replace(".bc","_{}.bc".format(self.jobid)))
        output = "{}{}".format(self.basepath,output.replace(".bc","_{}.bc".format(self.jobid)))
        if self.toIR(passes):
            self.toAssembly()
            with open("{}optimized_{}.ll".format(self.basepath,self.jobid),'r') as file:
                result = len(file.readlines())
        else:
            result = 0
        return result

    # To apply transformations
    def toIR(self, passes: str = '-O3') -> bool:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        result = self.allinone(passes)
        if not result:
            copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
            result = self.onebyone(passes)
        return result

    # To transform from LLVM IR to assembly code
    def toAssembly(self, source: str = "optimized.bc", output: str = "optimized.ll"):
        source = "{}{}".format(self.basepath,source.replace(".bc","_{}.bc".format(self.jobid)))
        output = "{}{}".format(self.basepath,output.replace(".ll","_{}.ll".format(self.jobid)))
        os.system("{}{} {}{} -o {}{}".format(self.llvmpath,self.llcexe,
                  self.basepath,source,self.basepath,output))

    # To apply transformations in one line
    def allinone(self, passes: str = '-O3') -> bool:
        result = True
        cmd = subprocess.Popen("{}{} {} {}optimized_{}.bc -o {}optimized_{}.bc".format(
                                self.llvmpath,self.optexe,passes,self.basepath,self.jobid,self.basepath,
                                self.jobid),shell=True,stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        cmd.wait(timeout=20)
        if cmd.returncode != 0:
            cmd.kill()
            result = False
        return result
    
    # To apply transformations one by one
    def onebyone(self, passes: str = '-O3') -> bool:
        result = True
        passeslist = passes.split(' ')
        self.onebyones += 1
        for llvm_pass in passeslist:
            cmd = subprocess.Popen("{}{} {} {}optimized_{}.bc -o {}optimized_{}.bc".format(
                                    self.llvmpath,self.optexe,llvm_pass, self.basepath,self.jobid,
                                    self.basepath,self.jobid),shell=True,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmd.wait(timeout=10)
            if cmd.returncode != 0:
                cmd.kill()
                result = False
        return result
        
    # To get the number of time onebyone is run
    def get_onebyone(self):
        return self.onebyones

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
                    