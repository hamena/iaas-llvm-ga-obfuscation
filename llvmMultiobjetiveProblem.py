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
                            source="polybench_small/polybench_small_original.bc" ,jobid='llvm_multiobjetive', useperf=False)
        self.number_of_variables = solution_length
        self.lower_bound = [0 for _ in range(self.number_of_variables)]
        self.upper_bound = [upper_bound for _ in range(self.number_of_variables)]
        self.obj_directions = [self.MINIMIZE, self.MAXIMIZE]
        self.obj_labels = ['runtime', 'codelines']
        self.number_of_objectives = 2
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
            with open("llvm_dictionary.data","r") as file:
                lines = file.readlines()
                for line in lines:
                    key = "["+"{}".format(line[:16])+"]"
                    value = "{}".format(line[17:])[:-1]
                    self.dictionary.update({key: value})

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

            solution.objectives[0] = self.llvm.get_codelines(passes=passes)
            solution.objectives[1] = self.llvm.get_runtime(passes=passes)
            self.dictionary.update({key: solution.objectives})
        else:
            solution.objectives[0] = value[0]
            solution.objectives[1] = value[1]
        if self.verbose: # En este bloque hay que controlar objectives[0] y objectives[1]
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
                    key = '{}'.format(keys).replace("[","").replace("]","")
                    key = '{}'.format(key).replace(", ",",")
                    file.write('{},{}\n'.format(key,values))
        return met
