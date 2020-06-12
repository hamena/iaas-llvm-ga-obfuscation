
"""
.. module:: Evaluator
   :platform: Unix, Windows
   :synopsis: Takes measures from a executable/assembly file

.. moduleauthor:: Jose Crespo Guerrero <jose.crespoguerrero@alum.uca.es>

"""

import os
import time

class Evaluator():

    def __init__(self, runs: int=1):
        self.runs = runs
        self.codelines = 0
        self.tags = 0
        self.unconditional_jmps = 0
        self.conditional_jmps = 0
        self.runtime = 0.0

    def evaluate(self, source_ll: str, source_exe: str):
        if not os.path.exists(source_ll):
            raise Exception("Source assembly file '{}' doesn't exists.")

        with open(source_ll,'r') as file:
            for line in file.readlines():
                self.codelines += 1
                self.tags += line[0]!='\t' and line[0]!='#'
                self.unconditional_jmps += line.count('jmp')
                self.conditional_jmps += line.count('jl')
                self.conditional_jmps += line.count('jge')

        if not os.path.exists(source_exe):
            raise Exception("Source executable file '{}' doesn't exists.")

        average = 0.0
        for _ in range(self.runs):
            start_time = time.time()
            os.system(source_exe)
            average += time.time() - start_time
        self.runtime = average / self.runs

    def reset(self):
        self.codelines = 0
        self.tags = 0
        self.unconditional_jmps = 0
        self.conditional_jmps = 0
        self.runtime = 0.0

    def get_runtime(self) -> float:
        return self.runtime

    def get_codelines(self) -> int:
        return self.codelines

    def get_tags(self) -> int:
        return self.tags

    def get_unconditional_jmps(self) -> int:
        return self.unconditional_jmps

    def get_conditional_jmps(self) -> int:
        return self.conditional_jmps

    def get_ratio_tags(self) -> float:
        return self.tags / self.codelines

    def get_ratio_unconditional_jmps(self) -> float:
        return self.unconditional_jmps / self.codelines

    def get_ratio_conditional_jmps(self) -> float:
        return self.conditional_jmps / self.codelines
