#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define rep(i, a, b) for (int i = a; i < int(b); ++i)

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

////////////////////////////////////////////////////////////////////////////////

#define THREAD_NUM 8

const int MAX = 1000000001;
uint_fast8_t sieve_vec[MAX];
int M = 0, N = MAX - 1;
bool only_count = true;

void sieve(int N) {
  sieve_vec[0] = sieve_vec[1] = 1;
  int _N2 = int(sqrt(N)) / 2;

#pragma omp parallel num_threads(THREAD_NUM) default(none)                     \
    firstprivate(_N2, N) shared(sieve_vec)
  {
#pragma omp for schedule(guided) nowait
    for (int j = 2 * 2; j < N; j += 2)
      sieve_vec[j] = 1;

#pragma omp for schedule(dynamic, 2) nowait
    for (int i = 3; i < _N2; i++) {
      int x = 2 * i - 3;
      if (sieve_vec[x] == 0) {
#pragma omp taskloop simd nogroup num_tasks(512)
        for (int j = 0; j < (N - x * x) / (x * 2) + 1; j++) {
          sieve_vec[x * x + j * x * 2] = 1;
        }
      }
    }
  }
}

void show(int m, int n) {
  int c = 0;
  rep(i, m, n) if (sieve_vec[i] == 0) {
    c++;
    if (!only_count) {
      printf("%8d ", i);
      if (c % 10 == 0)
        printf("\n");
    }
  }
  if (!only_count)
    printf("\n");
  printf("[COUNT] %d\n", c);
}

////////////////////////////////////////////////////////////////////////////////

int main(int argc, char *argv[]) {
  if (argc >= 3) {
    M = atoi(argv[1]);
    N = atoi(argv[2]);
    if (argc >= 4)
      if (argv[3][0] == 'p')
        only_count = false;
  } else {
    printf("./a.out M N p?\n");
    return 0;
  }

  printf("[SIEVE] M=%d N=%d only_count=%d\n", M, N, only_count);

  bench_t bench;
  bench.T1();
  sieve(N);
  bench.T2();
  show(M, N);
  bench.print();

  return 0;
}
