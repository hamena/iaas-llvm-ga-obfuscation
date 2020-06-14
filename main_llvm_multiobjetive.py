from jmetal.algorithm.multiobjective import NSGAII
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.operator import SBXCrossover, RandomSolutionSelection, IntegerPolynomialMutation
from jmetal.util.solution import get_non_dominated_solutions
from llvmMultiobjetiveProblem import llvmMultiobjetiveProblem
from jmetal.lab.visualization import Plot
import sys

### SETTINGS
config_max_epochs = int(sys.argv[1])
config_population_size = int(sys.argv[2])
config_offspring_population_size = int(sys.argv[3])
config_probability_mutation = 0.1
config_probability_crossover = 0.3
config_solution_length = int(sys.argv[4])
config_verbose = bool(sys.argv[5])

#config_max_epochs = 2
#config_population_size = 20
#config_offspring_population_size = 20
#config_probability_mutation = 0.1
#config_probability_crossover = 0.3
#config_solution_length = 40
#config_verbose = True

if __name__ == '__main__':

    # Problem set
    problem = llvmMultiobjetiveProblem(
        max_epochs=config_max_epochs,
        population_size=config_population_size,
        offspring_population_size=config_offspring_population_size,
        solution_length=config_solution_length,
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

    nds = get_non_dominated_solutions(algorithm.get_result())

    with open(f"{problem.config_to_str()}_results.data","w") as file:
        #Outputs
        file.write('\nSettings:')
        file.write(f'\n\tAlgorithm: {algorithm.get_name()}')
        file.write(f'\n\tProblem: {problem.get_name()}')
        file.write(f'\n\tComputing time: {algorithm.total_computing_time} seconds')
        file.write(f'\n\tMax epochs: {config_max_epochs}')
        file.write(f'\n\tPopulation size: {config_population_size}')
        file.write(f'\n\tOffspring population size: {config_offspring_population_size}')
        file.write(f'\n\tProbability mutation: {config_probability_mutation}')
        file.write(f'\n\tProbability crossover: {config_probability_crossover}')
        file.write(f'\n\tSolution length: {config_solution_length}')
        file.write('\nResults:')
        for sol in nds:
            file.write(f'\n\t\t{sol.variables}\t\t{sol.objectives}')

    print('\nSettings:')
    print(f'\tAlgorithm: {algorithm.get_name()}')
    print(f'\tProblem: {problem.get_name()}')
    print(f'\tComputing time: {algorithm.total_computing_time} seconds')
    print(f'\tMax epochs: {config_max_epochs}')
    print(f'\tPopulation size: {config_population_size}')
    print(f'\tOffspring population size: {config_offspring_population_size}')
    print(f'\tProbability mutation: {config_probability_mutation}')
    print(f'\tProbability crossover: {config_probability_crossover}')
    print(f'\tSolution length: {config_solution_length}')
    print(f'\nResults:')
    for sol in nds:
        print(f'\t\t{sol.variables}\t\t{sol.objectives}')

    plot_front = Plot(title='Pareto front aproximation', axis_labels=['runtime', 'codelines', 'tags', 'jumps', 'function_tags', 'calls'])
    plot_front.plot([nds], normalize=False, filename=f'{problem.config_to_str()}_pareto_front', format='eps')
    