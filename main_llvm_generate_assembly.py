"""
.. module:: main_llvm_generate_assembly
   :platform: Unix, Windows
   :synopsis: Generates llvm bc and assembly of a solution

.. moduleauthor:: Jose Crespo Guerrero <jose.crespoguerrero@alum.uca.es>

"""

from LlvmUtils import LlvmUtils
from LlvmUtils import LlvmFiles
from Evaluator import Evaluator

if __name__ == "__main__":

    llvmutils = LlvmUtils(llvmpath='/usr/bin/', clangexe='clang-10', optexe='opt-10', llcexe='llc-10')
    llvmfiles = LlvmFiles(basepath='./', source_bc='polybench_small/polybench_small_original.bc', jobid='solution')
    evaluator = Evaluator(runs=1)

    passes = [56, 77, 20, 25, 79, 1, 60, 68, 65, 35, 77, 25, 11, 52, 67, 66, 81, 24, 20, 77]
    
    strpasses = ""
    for s in passes:
        strpasses += f" {llvmutils.get_passes()[s]}"

    llvmutils.toIR(llvmfiles.get_original_bc(), llvmfiles.get_optimized_bc(), passes=strpasses)
    llvmutils.toAssembly(llvmfiles.get_optimized_bc(), llvmfiles.get_optimized_ll())

    solution = [0,0,0,0,0]
    evaluator.evaluate(source_ll=llvmfiles.get_optimized_ll(), source_exe=llvmfiles.get_optimized_exe())
    solution[0] = evaluator.get_runtime()
    solution[1] = evaluator.get_codelines()
    solution[2] = evaluator.get_tags()
    solution[3] = evaluator.get_unconditional_jmps()
    solution[4] = evaluator.get_conditional_jmps()
    evaluator.reset()

    print(solution)