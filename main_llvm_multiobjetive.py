from jmetal.algorithm.multiobjective import NSGAII
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.operator import SBXCrossover, RandomSolutionSelection, IntegerPolynomialMutation
from jmetal.util.solution import get_non_dominated_solutions
from llvmMultiobjetiveProblem import llvmMultiobjetiveProblem

### SETTINGS
config_max_evaluations = 30
config_population_size = 10
config_offspring_population_size = 10
config_probability_mutation = 0.1
config_probability_crossover = 0.3
config_solution_length = 10
config_dictionary_preloaded = False # True for load an initial dictionary
config_dictionary_name = "dictionary.data"
config_verbose = True


if __name__ == '__main__':

    # Problem set
    problem = llvmMultiobjetiveProblem(max_evaluations=config_max_evaluations,
        population_size=config_population_size,
        offspring_population_size=config_offspring_population_size,
        solution_length=config_solution_length,
        dictionary_preloaded=config_dictionary_preloaded,
        dictionary_name=config_dictionary_name,
        verbose=config_verbose)

    # Algorithm set
    algorithm = NSGAII(
        problem=problem,
        population_size=config_population_size,
        offspring_population_size=config_offspring_population_size,
        mutation=IntegerPolynomialMutation(config_probability_mutation),
        crossover=SBXCrossover(config_probability_crossover),
        selection=RandomSolutionSelection(),
        termination_criterion=problem
    )

    algorithm.run()

    with open("results.data","w") as file:
        #Outputs
        file.write('\nSettings:')
        file.write(f'\n\tAlgorithm: {algorithm.get_name()}')
        file.write(f'\n\tProblem: {problem.get_name()}')
        file.write(f'\n\tComputing time: {algorithm.total_computing_time} seconds')
        file.write(f'\n\tMax evaluations: {config_max_evaluations}')
        file.write(f'\n\tPopulation size: {config_population_size}')
        file.write(f'\n\tOffspring population size: {config_offspring_population_size}')
        file.write(f'\n\tProbability mutation: {config_probability_mutation}')
        file.write(f'\n\tProbability crossover: {config_probability_crossover}')
        file.write(f'\n\tSolution length: {config_solution_length}')
        file.write('\nResults:')
        for sol in get_non_dominated_solutions(algorithm.get_result()):
            file.write(f'\n\t\t{sol.variables}\t\t{sol.objectives}')

    print('\nSettings:')
    print(f'\tAlgorithm: {algorithm.get_name()}')
    print(f'\tProblem: {problem.get_name()}')
    print(f'\tComputing time: {algorithm.total_computing_time} seconds')
    print(f'\tMax evaluations: {config_max_evaluations}')
    print(f'\tPopulation size: {config_population_size}')
    print(f'\tOffspring population size: {config_offspring_population_size}')
    print(f'\tProbability mutation: {config_probability_mutation}')
    print(f'\tProbability crossover: {config_probability_crossover}')
    print(f'\tSolution length: {config_solution_length}')
    print(f'\nResults:')
    for sol in get_non_dominated_solutions(algorithm.get_result()):
        print(f'\t\t{sol.variables}\t\t{sol.objectives}')
