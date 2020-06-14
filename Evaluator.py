
"""
.. module:: Evaluator
   :platform: Unix, Windows
   :synopsis: Takes measures from a executable/assembly file

.. moduleauthor:: Jose Crespo Guerrero <jose.crespoguerrero@alum.uca.es>

"""

import sys
import os
import subprocess
import time

class Evaluator():

    def __init__(self, runs: int=1):
        self.runs = runs
        self.total_codelines = 0
        self.codelines = 0
        self.tags = 0
        self.function_tags = 0
        self.calls = 0
        self.unconditional_jmps = 0
        self.conditional_jmps = 0
        self.total_jmps = 0
        self.runtime = 0.0

    def evaluate(self, source_ll: str, source_exe: str):
        if not os.path.exists(source_ll):
            raise Exception("Source assembly file '{}' doesn't exists.")

        with open(source_ll,'r') as file:
            for line in file.readlines():
                self.total_codelines += 1
                self.tags += line[0]!='\t' and line[0]!=' ' and line[0]!='#' and line[0]=='.'
                self.function_tags += line[0]!='\t' and line[0]!=' ' and line[0]!='#' and line[0]!='.'
                self.calls += line.count('call')
                self.unconditional_jmps += line.count('jmp')
                self.conditional_jmps += line.count('jl')
                self.conditional_jmps += line.count('jge')
        self.total_jmps = self.conditional_jmps + self.unconditional_jmps
        self.codelines = self.total_codelines - self.tags - self.function_tags - self.calls - self.total_jmps
        
        #if not os.path.exists(source_exe):
        #    raise Exception("Source executable file '{}' doesn't exists.")

        #error = False
        #average = 0.0
        #for _ in range(self.runs):
        #    start_time = time.time()
        #    returncode = subprocess.run(source_exe).returncode
        #    if returncode:
        #        error = True
        #        break
        #    average += time.time() - start_time
        #if not error:
        #    self.runtime = average / self.runs
        #else:
        #    self.runtime = sys.maxsize

    def reset(self):
        self.total_codelines = 0
        self.codelines = 0
        self.tags = 0
        self.function_tags = 0
        self.calls = 0
        self.unconditional_jmps = 0
        self.conditional_jmps = 0
        self.total_jmps = 0
        self.runtime = 0.0

    def get_runtime(self) -> float:
        return self.runtime

    def get_codelines(self) -> int:
        return self.codelines

    def get_tags(self) -> int:
        return self.tags

    def get_function_tags(self) -> int:
        return self.function_tags

    def get_calls(self) -> int:
        return self.calls

    def get_unconditional_jmps(self) -> int:
        return self.unconditional_jmps

    def get_conditional_jmps(self) -> int:
        return self.conditional_jmps

    def get_total_jmps(self) -> int:
        return self.total_jmps

    def get_ratio_tags(self) -> float:
        return self.tags / self.total_codelines

    def get_ratio_function_tags(self) -> float:
        return self.function_tags / self.total_codelines

    def get_ratio_calls(self) -> float:
        return self.calls / self.total_codelines

    def get_ratio_unconditional_jmps(self) -> float:
        return self.unconditional_jmps / self.total_codelines

    def get_ratio_conditional_jmps(self) -> float:
        return self.conditional_jmps / self.total_codelines

    def get_ratio_total_jmps(self) -> int:
        return self.total_jmps / self.total_codelines
