#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// $ c=$'g++-9 -Wall -Wconversion -Wfatal-errors -g -std=c++17
//    \\n\t-fsanitize=undefined,address -Wno-builtin-macro-redefined'
// $ c -O3 -fopenmp hello_world.cc && ./a.out

// http://ppc.cs.aalto.fi/ch3/schedule/

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

long long w(int i) {
  volatile long long s = 0;
  for (int j = 0; j < (i * i * i) * 100000; j++)
    s += j;
  return s;
}

int main() {

  // [BASIC] /////////////////////////////

  int proc_num = omp_get_max_threads();
  printf("proc_num=%d\n", proc_num);
  omp_set_num_threads(proc_num);

  bench_t bench;
  bench.T1();

#pragma omp parallel
  { printf("Hello world! thread = %d\n", omp_get_thread_num()); }

  bench.T2();
  bench.print();

  // [SCHEDULE] /////////////////////////

  //          max
  //           ^
  //           | (static)
  //      load |     .
  //   balance |         . (guided)
  //           |
  //           | ideal        . (dynamic)
  //           x------------------> max
  //         min    scheduling
  //                  overhead

#define TEST_SCHEDULE(X)                                                       \
  {                                                                            \
    printf("\033[92m");                                                        \
    printf(X);                                                                 \
    printf("\033[m\n");                                                        \
    bench.T1();                                                                \
                                                                               \
    _Pragma("omp parallel default(none)") {                                    \
      int i, n = 10;                                                           \
                                                                               \
      _Pragma(X) for (i = 0; i < n; i++) {                                     \
        (void)w(i); /* tak aby bylo widac roznice */                           \
        printf("\ti = %d; thread = %d\n", i, omp_get_thread_num());            \
      }                                                                        \
    }                                                                          \
                                                                               \
    bench.T2();                                                                \
    bench.print();                                                             \
  }

  // podział pracy domyślny
  TEST_SCHEDULE("omp for")

  // podział pracy statyczny blokowy
  TEST_SCHEDULE("omp for schedule(static, 3)")

  // podział pracy statyczny cykliczny
  TEST_SCHEDULE("omp for schedule(static, 1)")

  // podziłał pracy dynamiczny domyślny i sparametryzowany
  TEST_SCHEDULE("omp for schedule(dynamic)")
  TEST_SCHEDULE("omp for schedule(dynamic, 3)")

  // podział dynamiczny - sterowany
  TEST_SCHEDULE("omp for schedule(guided)")

  // [SHARING/RACE] /////////////////////////

  int S, k;
  printf("\nS = 24497550 (powinno wynosic)\n"); // random?

  S = 0;
  k = 0;
#pragma omp parallel for
  for (int i = 1; i < 100; ++i) {
    k = i * i;
    printf("+"); // trick: teraz mamy nie deterministyczny!
    S += i * (k - 1);
    k -= i * i;
  }

  printf("@1 S = %d\n", S); // random?

  S = 0;
  k = 0;
#pragma omp parallel for
  for (int i = 1; i < 100; ++i) {
#pragma omp critical
    {
      k = i * i;
      printf("+");
      S += i * (k - 1);
    }
    k -= i * i;
  }

  printf("@2 S = %d\n", S); // 24497550
}
