#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Q: ile wynosi "cache line"/L1?

// A: z eksperymentu wynika ze MEMSHIFT=7 (bo czasy sa takie jak w PI4)
//    a wiec dlugosc linii wynosi [8 * 8 bajtow = 64] na dane
//    (co jest zgodne z moja architektura komputera)

/*
threads_num=2

MEMSHIFT=0
  0 -> vsum[ 0]   1 -> vsum[ 1]
<time.h> time=8.232575
 <omp.h> time=4.170651

MEMSHIFT=1
  0 -> vsum[ 0]   1 -> vsum[ 2]
<time.h> time=7.778722
 <omp.h> time=3.921388

MEMSHIFT=2
  0 -> vsum[ 0]   1 -> vsum[ 3]
<time.h> time=7.801917
 <omp.h> time=3.932336

MEMSHIFT=3
  0 -> vsum[ 0]   1 -> vsum[ 4]
<time.h> time=7.810248
 <omp.h> time=3.949122

MEMSHIFT=4
  0 -> vsum[ 0]   1 -> vsum[ 5]
<time.h> time=8.097199
 <omp.h> time=4.086339

MEMSHIFT=5
  0 -> vsum[ 0]   1 -> vsum[ 6]
<time.h> time=7.827552
 <omp.h> time=3.954192

MEMSHIFT=6
  0 -> vsum[ 0]   1 -> vsum[ 7]
<time.h> time=7.848424
 <omp.h> time=3.952066

MEMSHIFT=7
  0 -> vsum[ 0]   1 -> vsum[ 8]
<time.h> time=5.211482
 <omp.h> time=2.619698

MEMSHIFT=8
  0 -> vsum[ 0]   1 -> vsum[ 9]
<time.h> time=5.438142
 <omp.h> time=2.752816

MEMSHIFT=9
  0 -> vsum[ 0]   1 -> vsum[10]
<time.h> time=5.214670
 <omp.h> time=2.624130

MEMSHIFT=10
  0 -> vsum[ 0]   1 -> vsum[11]
<time.h> time=5.413838
 <omp.h> time=2.740313

MEMSHIFT=11
  0 -> vsum[ 0]   1 -> vsum[12]
<time.h> time=5.261158
 <omp.h> time=2.648972

MEMSHIFT=12
  0 -> vsum[ 0]   1 -> vsum[13]
<time.h> time=5.504936
 <omp.h> time=2.802603

MEMSHIFT=13
  0 -> vsum[ 0]   1 -> vsum[14]
<time.h> time=5.456885
 <omp.h> time=2.780098

MEMSHIFT=14
  0 -> vsum[ 0]   1 -> vsum[15]
<time.h> time=5.604465
 <omp.h> time=2.878687

MEMSHIFT=15
  0 -> vsum[ 0]   1 -> vsum[16]
<time.h> time=5.297931
 <omp.h> time=2.668634
*/

#define THREADS_POLICY 2

struct bench_t {
  clock_t C1, C2;
  double O1, O2;

  void T1() {
    this->C1 = clock();
    this->O1 = omp_get_wtime();
  }

  void T2() {
    this->C2 = clock();
    this->O2 = omp_get_wtime();
  }

  void print() {
    printf("<time.h> time=%f\n", ((double)(C2 - C1) / CLOCKS_PER_SEC));
    printf(" <omp.h> time=%f\n", ((double)(O2 - O1)));
  }
};

#define MEMSHIFT 16
volatile double vsum[THREADS_POLICY * (MEMSHIFT + 1)] = {0};

int main(int argc, char *argv[]) {
  int threads_num = THREADS_POLICY;
  printf("threads_num=%d\n", threads_num);
  omp_set_num_threads(threads_num);

  for (int memshift = 0; memshift < MEMSHIFT; memshift++) {
    printf("\n\033[92mMEMSHIFT=%d\033[m\n", memshift);
    for (int i = 0; i < THREADS_POLICY; i++)
      printf(" %2d -> vsum[%2d] ", i, i + i * memshift);
    printf("\n");

    double pi, sum = 0.0;

    for (int i = 0; i < THREADS_POLICY * (MEMSHIFT + 1); i++)
      vsum[i] = 0;

    bench_t bench;
    bench.T1();

#define NUM_STEPS 1000000000

#pragma omp parallel default(none) shared(vsum, memshift)
    {
      double step2 = (1. / NUM_STEPS) * (1. / NUM_STEPS);
      int idx = omp_get_thread_num();

#pragma omp for schedule(static, 1) nowait
      for (int i = 0; i < NUM_STEPS; i++)
        vsum[idx + idx * memshift] +=
            4.0 / (1. + (i + .5) * (i + .5) * (step2));
    }

    double step = 1. / NUM_STEPS;
    for (int i = 0; i < THREADS_POLICY * (MEMSHIFT + 1); i++)
      sum += vsum[i];
    pi = sum * step;

    bench.T2();
    bench.print();
  }

  return 0;
}
