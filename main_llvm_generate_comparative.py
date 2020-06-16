"""
.. module:: main_llvm_generate_assembly
   :platform: Unix, Windows
   :synopsis: Generates llvm bc and assembly of a solution

.. moduleauthor:: Jose Crespo Guerrero <jose.crespoguerrero@alum.uca.es>

"""

from LlvmUtils import LlvmUtils
from LlvmUtils import LlvmFiles
from Evaluator import Evaluator
import matplotlib.pyplot as plt

def to_int_array(strarray: str):
    strarray = strarray[1:-1]
    splitted = strarray.split(sep=',')
    array = []
    for s in splitted:
        array.append(int(s))
    return array

if __name__ == "__main__":

    llvmutils = LlvmUtils(llvmpath='/usr/bin/', clangexe='clang-10', optexe='opt-10', llcexe='llc-10')
    llvmfiles = LlvmFiles(basepath='./', source_bc='polybench_small/polybench_small_original.bc', jobid='solution')
    evaluator = Evaluator(runs=10)

    plot_labels = ['total codelines', 'codelines', 'labels', 
    'conditional jumps', 'unconditional jumps', 'function labels', 'function calls']

    llvmutils.toAssembly(llvmfiles.get_original_bc(), "original.ll")
    llvmutils.toExecutable(llvmfiles.get_original_bc(), "original.o")
    evaluator.evaluate("original.ll", "./original.o")

    original_results = []
    #original_results.append(evaluator.get_runtime())
    original_results.append(evaluator.get_total_codelines())
    original_results.append(evaluator.get_codelines())
    original_results.append(evaluator.get_tags())
    #original_results.append(evaluator.get_total_jmps())
    original_results.append(evaluator.get_conditional_jmps())
    original_results.append(evaluator.get_unconditional_jmps())
    original_results.append(evaluator.get_function_tags())
    original_results.append(evaluator.get_calls())
    evaluator.reset()
    
    allpasses = []

    with open('20_20_20/20_20_20_25_results.csv', 'r') as file:
        for line in file.readlines():
            line = line[:-1]
            keyvalue = line.split(sep=';')
            passes = to_int_array(keyvalue[0])
            fitness = to_int_array(keyvalue[1])

            strpasses = ""
            for s in passes:
                strpasses += f" {LlvmUtils.get_passes()[s]}"
            
            allpasses.append(strpasses)
            #print(strpasses)

    count = 1
    for strpasses in allpasses:

        llvmutils.toIR(llvmfiles.get_original_bc(), f"optimized_{count}.bc", strpasses)
        llvmutils.toAssembly(f"optimized_{count}.bc", f"optimized_{count}.ll")
        llvmutils.toExecutable(f"optimized_{count}.bc", f"optimized_{count}.o")

        evaluator.evaluate(f"optimized_{count}.ll", f"./optimized_{count}.o")
        optimized_results = []
        #optimized_results.append(evaluator.get_runtime())
        optimized_results.append(evaluator.get_total_codelines())
        optimized_results.append(evaluator.get_codelines())
        optimized_results.append(evaluator.get_tags())
        #optimized_results.append(evaluator.get_total_jmps())
        optimized_results.append(evaluator.get_conditional_jmps())
        optimized_results.append(evaluator.get_unconditional_jmps())
        optimized_results.append(evaluator.get_function_tags())
        optimized_results.append(evaluator.get_calls())
        evaluator.reset()

        diff = []
        for i in range(0, len(optimized_results)):
            diff.append(optimized_results[i] - original_results[i])

        print(f"Individual {count} passes: {strpasses}")
        
        #plt.bar(plot_labels, diff)
        #plt.plot(plot_labels, optimized_results)
        #plt.show()

        count += 1
