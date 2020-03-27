#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Q: w jaki sposób można na poziomie wątku zapewnić atomowość
//    (niepodzielność) uaktualnienia zmiennej współdzielonej w systemie.

// A: w OpenMP mozemy uzyc "atomic"/"reduction" lub stworzyc "critical" section
//    jednak z doswiadczenia stworzenie "#pragma omp critical"
//    jest duzo bardziej kosztowne niz wskazanie "#pragma omp atomic"
//    na dana pojedyncza operacje
//    ---
//    jesli nie chcemy korzystac z takich "wbudowanych" podejsc
//    mozemy zastosowac vectoryzacje (ten pomysl przejawia sie w PI6)
//    trzeba jednak pamietac o false sharingu

/*
threads_num=4
<time.h> time=26.007221
 <omp.h> time=7.328063
Wartosc liczby PI wynosi  3.141592653590
*/

// a) liczba procesorow logicznych
#define THREADS_LOGIC 4 /* $ sysctl -n hw.logicalcpu */
// b) liczba procesorow fizycznych
#define THREADS_PHYSICAL 2 /* $ sysctl -n hw.physicalcpu */
// c) polowa liczby procesorow fizycznych
#define THREADS_HALF THREADS_PHYSICAL / 2

#define THREADS_POLICY THREADS_LOGIC

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

int main(int argc, char *argv[]) {
  int threads_num = THREADS_POLICY;
  printf("threads_num=%d\n", threads_num);
  omp_set_num_threads(threads_num);

  double pi, sum = 0.0;

  bench_t bench;
  bench.T1();

#define NUM_STEPS 100000000

#pragma omp parallel default(none) shared(sum)
  {
    double step = 1. / (double)NUM_STEPS;

#pragma omp for schedule(guided)
    for (int i = 0; i < NUM_STEPS; i++) {
      double x = (i + .5) * step;
#pragma omp atomic
      sum += 4.0 / (1. + x * x);
    }
  }

  double step = 1. / NUM_STEPS;
  pi = sum * step;

  bench.T2();
  bench.print();

  printf("Wartosc liczby PI wynosi %15.12f\n", pi);

  return 0;
}
