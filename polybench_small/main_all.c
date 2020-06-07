/* Programa que se encarga de ejecutar todos los benchmarks seleccionados
   secuencialmente. */
#define MINI_DATASET
#include "2mm.h"
#include "3mm.h"
#include "atax.h"
#include "bicg.h"
#include "cholesky.h"
#include "doitgen.h"
#include "gemm.h"
#include "gemver.h"
#include "gesummv.h"
#include "mvt.h"
#include "symm.h"
#include "syr2k.h"
#include "syrk.h"
#include "trisolv.h"
#include "trmm.h"

/* Minería de datos */
#include "correlation.h"

//#include <stdio.h>

extern int main_correlation();
extern int main_2mm();
extern int main_3mm();
extern int main_atax();
extern int main_bicg();
extern int main_cholesky();
extern int main_doitgen();
extern int main_gemm();
extern int main_gemver();
extern int main_gesummv();
extern int main_mvt();
extern int main_symm();
extern int main_syr2k();
extern int main_syrk();
extern int main_trisolv();
extern int main_trmm();

int main()
{
    int i;
    for(i=0;i<10;i++)
    {
        /* Minería de datos */
        main_correlation();

        main_2mm();
        main_3mm();
        main_atax();
        main_bicg();
        main_cholesky();
        main_doitgen();
        main_gemm();
        main_gemver();
        main_gesummv();
        main_mvt();
        main_symm();
        main_syr2k();
        main_syrk();
        main_trisolv();
        main_trmm();
    }
    return 0;
}