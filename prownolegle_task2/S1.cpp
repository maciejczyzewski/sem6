#include <cstring>
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <vector>

#define rep(i, a, b) for (int i = a; i < int(b); ++i)

const int MAX = int(10e8);

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ALGORITHM START <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
std::vector<uint_fast8_t> W, S;
std::vector<uint_fast32_t> smallPrimes = std::vector<uint_fast32_t>(), result = std::vector<uint_fast32_t>();

void generateSmallPrimes(int n)
{
	S = std::vector<uint_fast8_t>(n, 0);
	for (int i = 2; i * i <= n; i++)
	{
		if (S[i] != 1)
			for (int j = i * i; j <= n; j += i)
			{
				S[j] = 1;
			}
	}

	rep(i, 2, n) if (S[i] == 0) smallPrimes.push_back(i);
}

void sieve(int M, int N, int num_threads) {

	generateSmallPrimes(N);
	W = std::vector<uint_fast8_t>(N, 0);
	W[0] = W[1] = 1;

#pragma omp parallel shared(smallPrimes, W, N) num_threads(num_threads)
	{
#pragma omp for schedule(guided, 50)
		for (int i = 0; i < smallPrimes.size(); i++)
		{
			for (int j = smallPrimes[i]; j <= N / smallPrimes[i]; j++)
			{
				W[smallPrimes[i] * j] = 1;
			}
		}
	}

	rep(i, M, N) if (W[i] == 0) result.push_back(i);
}

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ALGORITHM END <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> BENCHMARKS START <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

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

void show(int m, int n, bool only_count) {
	int c = 0;
	rep(i, 0, result.size()) {
		if (int(result[i]) < m)
			continue;
		c++;
		if (!only_count) {
			printf("%8d ", result[i]);
			if (c % 10 == 0)
				printf("\n");
		}
	}
	if (!only_count)
		printf("\n");
	printf("[COUNT] %d\n", c);
}

int main(int argc, char* argv[]) {
	int M = 0, N = MAX - 1, P = 8;
	bool only_count = true;

	if (argc >= 3) {
		M = atoi(argv[1]);
		N = atoi(argv[2]);
		if (argc >= 4)
			if (argv[3][0] == 'p')
				only_count = false;
		if (argc >= 5)
			P = atoi(argv[4]);
	}
	else {
		printf("./a.out M N p?\n");
		return 0;
	}

	printf("[SIEVE] M=%d N=%d only_count=%d threads=%d\n", M, N, only_count, P);

	bench_t bench;
	bench.T1();
	sieve(M, N, P);
	bench.T2();
	show(M, N, only_count);
	bench.print();

	return 0;
}
