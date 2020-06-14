import sys
import os

from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution

from LlvmUtils import LlvmUtils
from LlvmUtils import LlvmFiles
from Evaluator import Evaluator

class llvmMultiobjetiveProblem(IntegerProblem):

    def __init__(self, max_epochs: int = 500, filename: str = None, solution_length: int = 100, population_size = int, 
                offspring_population_size = int, verbose: bool = True, upper_bound : int = 86):

        self.llvm = LlvmUtils(llvmpath='/usr/bin/', clangexe='clang-10', optexe='opt-10', llcexe='llc-10')
        self.llvmfiles = LlvmFiles(basepath='./', source_bc='polybench_small/polybench_small_original.bc', 
                                jobid=f'{population_size}_{offspring_population_size}_{solution_length}')
        self.evaluator = Evaluator(runs=0)
        self.number_of_variables = solution_length
        self.lower_bound = [0 for _ in range(self.number_of_variables)]
        self.upper_bound = [upper_bound for _ in range(self.number_of_variables)]
        self.obj_labels = ['codelines', 'tags', 'jumps', 'function_tags', 'calls']
        self.obj_directions = [self.MAXIMIZE, self.MINIMIZE, self.MINIMIZE, self.MINIMIZE, self.MINIMIZE]
        self.number_of_objectives = 5
        self.number_of_constraints = 0
        self.max_epochs = max_epochs
        self.evaluations = 0
        self.epoch = 1
        self.phenotype = 0
        self.population_size = population_size
        self.offspring_population_size = offspring_population_size
        self.dictionary = dict()
        self.verbose = verbose
        self.preloaded_dictionary = f"{self.number_of_variables}_dictionary.data"
        if os.path.exists(self.preloaded_dictionary):
            with open(self.preloaded_dictionary,"r") as file:
                print(f"reading '{self.preloaded_dictionary}'...")
                for line in file.readlines():
                    line = line[:-1] # \n
                    keyvalue = line.split(sep=";")
                    self.dictionary.update({keyvalue[0]:keyvalue[1]})

    def get_name(self):
        return 'Llvm Multiobjective Problem'

    def config_to_str(self):
        return f"{self.population_size}_{self.offspring_population_size}_{self.number_of_variables}_{self.max_epochs}"

    def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
        self.phenotype +=1
        limit = [self.offspring_population_size if self.epoch != 1 else self.population_size]
        if self.phenotype%(limit[0]+1) == 0:
            self.epoch += 1
            self.phenotype = 1
        key = f"{solution.variables}"
        value = self.dictionary.get(key)
        if value == None:
            # Decoding
            passes = ""
            for i in range(self.number_of_variables):
                passes += f" {self.llvm.get_passes()[solution.variables[i]]}"

            # Optimize and generate resources
            self.llvm.toIR(self.llvmfiles.get_original_bc(), self.llvmfiles.get_optimized_bc(), passes=passes)
            self.llvm.toExecutable(self.llvmfiles.get_optimized_bc(), self.llvmfiles.get_optimized_exe())
            self.llvm.toAssembly(self.llvmfiles.get_optimized_bc(), self.llvmfiles.get_optimized_ll())

            # Get measures
            self.evaluator.evaluate(source_ll=self.llvmfiles.get_optimized_ll(), source_exe=self.llvmfiles.get_optimized_exe())
            solution.objectives[0] = self.evaluator.get_codelines()
            solution.objectives[1] = self.evaluator.get_tags()
            solution.objectives[2] = self.evaluator.get_total_jmps()
            solution.objectives[3] = self.evaluator.get_function_tags()
            solution.objectives[4] = self.evaluator.get_calls()
            self.dictionary.update({key: solution.objectives})
            self.evaluator.reset()
        else:
            # Get stored value
            solution.objectives[0] = value[0]
            solution.objectives[1] = value[1]
            solution.objectives[2] = value[2]
            solution.objectives[3] = value[3]
            solution.objectives[4] = value[4]
        
        if self.verbose:
            print("evaluated solution {:3} from epoch {:3} : variables={}, fitness={}"\
                .format(self.phenotype,self.epoch,solution.variables,solution.objectives))
        return solution

    ### FOR TERMINATION CRITERION ###
    def update(self, *args, **kwargs):
        self.evaluations = kwargs['EVALUATIONS']

    ### FOR TERMINATION CRITERION ###
    @property
    def is_met(self):
        met = self.epoch >= self.max_epochs
        if self.phenotype*self.epoch % 100 == 0 or met:
            with open(self.preloaded_dictionary, "w") as file:
                for keys,values in self.dictionary.items():
                    file.write('{};{}\n'.format(keys,values))
        return met
