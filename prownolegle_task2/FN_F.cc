#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <vector>

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

#define THREAD_NUM 8
const int MAX = int(10e8);
int M = 0, N = MAX - 1;
bool only_count = true;

////////////////////////////////////////////////////////////////////////////////

uint_fast8_t sieve_vec[MAX];
uint_fast32_t primes_vec[int(MAX * 0.075)], primes_size = 0;

////////////////////////////////////////////////////////////////////////////////

#define uint64 unsigned long long

bench_t bench;

bool is_prime(uint64 n) {
  uint64 end = (uint64)sqrt(n);

  for (uint64 i = 0; primes_vec[i] <= end; i++) {
    if (n % primes_vec[i] == 0)
      return false;
  }

  return true;
}

inline int fast_mod(const int input, const int ceil) {
  return input >= ceil ? input % ceil : input;
}

////////////////////////////////////////////////////////////////////////////////

void __fn_1(int block_size, int shift, int N) {
#pragma omp parallel num_threads(THREAD_NUM) default(none)                     \
    firstprivate(block_size, shift, N) shared(sieve_vec, primes_vec)
  {
    rep(idx, 0, THREAD_NUM) {
      rep(i, shift + (idx * block_size), shift + (idx + 1) * block_size) {
        int p = primes_vec[i];
#pragma omp for schedule(guided) nowait
        for (int j = p * p; j <= N; j += p)
          sieve_vec[j] = 1;
      }
    }
  }
}

void __fn_2(int block_size, int shift, int N) {
#pragma omp parallel for num_threads(THREAD_NUM) default(none)                 \
    firstprivate(block_size, shift, N) shared(sieve_vec, primes_vec)           \
        collapse(2)
  rep(idx, 0, THREAD_NUM) {
    rep(i, 0, block_size) {
      int p = primes_vec[shift + idx * block_size + i];
#pragma taskloop
      for (int j = p * p; j <= N; j += p)
        sieve_vec[j] = 1;
    }
  }
}

void __fn_3(int block_size, int shift, int N) {
#pragma omp parallel num_threads(THREAD_NUM) default(none)                     \
    firstprivate(block_size, shift, N) shared(sieve_vec, primes_vec)
  {
    int idx = omp_get_thread_num();
    rep(i, shift + (idx * block_size), shift + (idx + 1) * block_size) {
      int p = primes_vec[i];
      for (int j = p * p; j <= N; j += p)
        sieve_vec[j] = 1;
    }
  }
}

////////////////////////////////////////////////////////////////////////////////

void sieve(int N) {
  omp_set_dynamic(0); // FIXME
  omp_set_num_threads(THREAD_NUM);

  primes_vec[primes_size++] = 2;
  for (uint64 i = 3; i <= sqrt(N) * 1.01; i += 2)
    if (is_prime(i))
      primes_vec[primes_size++] = i;

  int shift = 0, block_size;
  block_size = (primes_size - shift) / (THREAD_NUM);
  bench.T1();

  // __fn_1(block_size, shift, N);
  // __fn_2(block_size, shift, N);
  __fn_3(block_size, shift, N);

  bench.T2();
  rep(i, primes_vec[primes_size - 1] + 1, N) if (sieve_vec[i] == 0)
      primes_vec[primes_size++] = i;
}

void show(int m, int n) {
  int c = 0;
  rep(i, 0, primes_size) {
    if (int(primes_vec[i]) < m)
      continue;
    c++;
    if (!only_count) {
      printf("%8d ", primes_vec[i]);
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

  sieve(N);
  show(M, N);
  bench.print();

  return 0;
}
