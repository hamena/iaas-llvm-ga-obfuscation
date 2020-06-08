import sys

from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution

from LlvmUtils import LlvmUtils

class llvmMultiobjetiveProblem(IntegerProblem):

    def __init__(self, is_minimization: bool = True, max_evaluations: int = 25000,
                 from_file: bool = False, filename: str = None, solution_length: int = 100,
                 population_size = int, offspring_population_size = int, verbose: bool = True, upper_bound : int = 86, 
                 dictionary_preloaded: bool = True, dictionary_name: str = 'llvm_dictionary.data'):

        self.llvm = LlvmUtils(llvmpath='/usr/bin/', clangexe="clang-10", optexe="opt-10", llcexe="llc-10", 
                            source="polybench_small/polybench_small_original.bc" ,jobid='llvm_multiobjetive')
        self.number_of_variables = solution_length
        self.lower_bound = [0 for _ in range(self.number_of_variables)]
        self.upper_bound = [upper_bound for _ in range(self.number_of_variables)]
        self.obj_labels = ['runtime', 'codelines', 'jmp', 'jl_jge']
        self.obj_directions = [self.MINIMIZE, self.MAXIMIZE, self.MAXIMIZE, self.MINIMIZE]
        self.number_of_objectives = 4
        self.number_of_constraints = 0
        self.is_minimization = is_minimization
        self.max_evaluations = max_evaluations
        self.evaluations = 0
        self.epoch = 1
        self.phenotype = 0
        self.population_size = population_size
        self.offspring_population_size = offspring_population_size
        self.dictionary = dict()
        self.verbose = verbose
        self.dictionary_preloaded = dictionary_preloaded
        if self.dictionary_preloaded:
            with open(f"{dictionary_name}","r") as file:
                for line in file.readlines():
                    line = line[:-1]
                    keyvalue = line.split(sep=";")
                    print(f"line: {line}")
                    print(f"key: {keyvalue[0]}")
                    print(f"value: {keyvalue[1]}")
                    self.dictionary.update({keyvalue[0]:keyvalue[1]})

    def get_name(self):
        return 'Llvm Multiobjetive Problem'

    def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
        self.phenotype +=1
        limit = [self.offspring_population_size if self.epoch != 1 else self.population_size]
        if self.phenotype%(limit[0]+1) == 0:
            self.epoch += 1
            self.phenotype = 1
        key = "{}".format(solution.variables)
        value = self.dictionary.get(key)
        if value == None:
            # Decoding
            passes = ""
            for i in range(self.number_of_variables):
                passes += " {}".format(self.llvm.get_passes()[solution.variables[i]])

            # Optimize and generate resources
            self.llvm.toIR(passes=passes)
            self.llvm.toExecutable()
            self.llvm.toAssembly()

            # Get measures
            solution.objectives[0] = self.llvm.get_runtime(passes=passes)
            solution.objectives[1] = self.llvm.get_codelines()
            solution.objectives[2] = self.llvm.get_jmp()
            solution.objectives[3] = self.llvm.get_conditional_jumps()
            self.dictionary.update({key: solution.objectives})
        else:
            solution.objectives[0] = value[0]
            solution.objectives[1] = value[1]
            solution.objectives[2] = value[2]
            solution.objectives[3] = value[3]
        if self.verbose:
            strfitness=f"{solution.objectives}'"
            print("evaluated solution {:3} from epoch {:3} : variables = {}, fitness = {}"\
                   .format(self.phenotype,self.epoch,solution.variables,strfitness))
            if self.phenotype == 1 and self.epoch == 1 :
                with open(f"solutions_{self.population_size}_{self.offspring_population_size}.data","w") as file:
                    file.write("{} {} {} {}\n".format("iter","epoch","variables","fitness"))
            with open(f"solutions_{self.population_size}_{self.offspring_population_size}.data","a") as file:
                file.write("{} {} {} {}\n"\
                   .format(self.phenotype,self.epoch,solution.variables,strfitness))
        return solution

    def get_onebyone(self):
        return self.llvm.get_onebyone()

    ### FOR TERMINATION CRITERION ###
    def update(self, *args, **kwargs):
        self.evaluations = kwargs['EVALUATIONS']

    ### FOR TERMINATION CRITERION ###
    @property
    def is_met(self):
        met = self.evaluations >= self.max_evaluations
        if self.phenotype*self.epoch % 100 == 0 or met:
            filename = "new_dictionary_{}_{}_{}.data".format(self.population_size,
                        self.offspring_population_size, self.phenotype*self.epoch)
            with open(filename,"w") as file:
                for keys,values in self.dictionary.items():
                    file.write('{};{}\n'.format(keys,values))
        return met
