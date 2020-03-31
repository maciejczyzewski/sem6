#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Q: dlaczego linuxowy czas uzycia procesor rozni sie od (wall clock)
//    i wyjasnic przyczyne.

// A: wall clock to czas jaki minal od punktu p1 do p2 (real clock),
//    natomiast clock() time (czyli system-cpu time) to
//    czas ktory program spedzil na procesorze (kernel code).
//    Wiec jak cos wywlaszczylo na 5 sec nasz program,
//    to ten czas nie bedzie liczony.

/*
<time.h> time=0.494735
 <omp.h> time=0.496406
Wartosc liczby PI wynosi  3.141592653590
*/

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

long long num_steps = 100000000;
double step;

int main(int argc, char *argv[]) {

  double x, pi, sum = 0.0;
  int i;
  step = 1. / (double)num_steps;

  bench_t bench;
  bench.T1();

  for (i = 0; i < num_steps; i++) {
    x = (i + .5) * step;
    sum = sum + 4.0 / (1. + x * x);
  }

  pi = sum * step;

  bench.T2();
  bench.print();

  printf("Wartosc liczby PI wynosi %15.12f\n", pi);

  return 0;
}
