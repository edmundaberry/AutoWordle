#ifndef FASTWORDLE_H
#define FASTWORDLE_H

#include <stdint.h>

void c_get_result(int32_t* guess_code,
		  int32_t* secret_code,
		  int32_t* result,
		  long n_letters);

void c_get_results(int32_t* guess_codes,
		   int32_t* secret_code,
		   int32_t* results,
		   long n_letters,
		   long n_guesses);

double c_get_score(int32_t* guess_codes,
		   int32_t* secret_code,
		   long n_letters,
		   long n_guesses);

double c_get_best_score(int32_t* guess_codes,
			int32_t* secret_code,
			int32_t* best_code,
			long n_letters,
			long n_guesses,
			long n_secrets);

#endif
