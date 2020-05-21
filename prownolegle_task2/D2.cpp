#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <math.h>
#include <omp.h>
#include <algorithm>
#include <time.h>

#define USE_THREADS 8
#define rep(i, a, b) for (int i = a; i < int(b); ++i)

const int MAX = int(10e8);

std::vector<int> result;

std::vector<int> naiveParallelThird(int begin, int end, int num_threads)
{
	omp_set_num_threads(num_threads);

	begin = fmax(2, begin);

	std::vector<int> result_loc;
	int number;
	int divider;

#pragma omp parallel default(none) shared(result_loc, begin, end)
	{
		std::vector<int> primes;

#pragma omp for schedule(guided) private(number, divider)
		for (number = begin; number <= end; number++)
		{
			for (divider = 2; divider <= sqrt(number); divider++)
				if (number % divider == 0)
					goto outer;

			primes.push_back(number);
		outer:;
		}

#pragma omp critical
		result_loc.insert(result_loc.end(), primes.begin(), primes.end());
	}

	result = result_loc;
	return result_loc;
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
	naiveParallelThird(M, N, P);
	bench.T2();
	show(M, N, only_count);
	bench.print();

	return 0;
}
