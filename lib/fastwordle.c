#include "fastwordle.h"

enum Status {
  RIGHT_PLACE = 1,
  WRONG_PLACE = 2,
  NOT_PRESENT = 3,
  EMPTY = 4
};

double c_get_best_score(int32_t* guess_codes,
			int32_t* secret_codes,
			int32_t* best_code,
			long n_letters,
			long n_guesses,
			long n_secrets) {

  // Initialize pointer
  int32_t* secret_code = secret_codes;

  // Initialize score
  double best_score = -1.0;

  // Loop over candidates  
  for (long i_secret = 0; i_secret < n_secrets; ++i_secret){

    // Get the score
    double this_score = c_get_score(guess_codes,
				    secret_code,
				    n_letters,
				    n_guesses);

    // Is this the best score?
    if (this_score > best_score){

      // Save the best code
      for (long i_letter = 0; i_letter < n_letters; ++i_letter){
	best_code[i_letter] = secret_code[i_letter];
      }

      // New best score
      best_score = this_score;
    }
    
    // Increment pointer
    secret_code += n_letters;

  }

  // Return
  return best_score;

}

double c_get_score(int32_t* guess_codes,
		   int32_t* secret_code,
		   long n_letters,
		   long n_guesses) {

  // Initialize pointer
  int32_t* guess_code = guess_codes;
  int32_t  result[n_letters];

  // Initialize score
  int i_score = 0;

  // Loop over candidates
  for (long i = 0; i < n_guesses; ++i){

    // Run individual result
    c_get_result(guess_code,
		 secret_code,
		 result,
		 n_letters);

    // Get score
    for (long j = 0; j < n_letters; ++j){
      if ((result[j] == RIGHT_PLACE) ||
	  (result[j] == WRONG_PLACE)) {
	++i_score;
      }
    }

    // Increment pointer
    guess_code += n_letters;    

  }

  double score = i_score;
  score /= n_guesses;
  return score;
}

void c_get_results(int32_t* guess_codes,
		   int32_t* secret_code,
		   int32_t* results,
		   long n_letters,
		   long n_guesses) {

  // Initialize pointers
  int32_t* guess_code = guess_codes;
  int32_t* result     = results;

  // Loop over candidates
  for (long i = 0; i < n_guesses; ++i){

    // Run individual result
    c_get_result(guess_code,
		 secret_code,
		 result,
		 n_letters);

    // Increment pointers
    guess_code += n_letters;
    result     += n_letters;

  }

  return;

}

void c_get_result (int32_t* guess_code,
		   int32_t* secret_code,
		   int32_t* result,
		   long n) {

  // Right place first
  for (long i = 0; i < n; ++i){

    // Default to NOT PRESENT
    result[i] = NOT_PRESENT;

    // Right place?
    if (guess_code[i] == secret_code[i]){
      result[i] = RIGHT_PLACE;
      continue;
    }
  }
  
  // Outer loop
  for (long i = 0; i < n; ++i){

    // Initialize counters
    long n_right  = 0;
    long n_secret = 0;
    long n_guess  = 0;

    // Inner loop to set counters
    for (long j = 0; j < n; ++j){

      // How many times in the right place?
      if (guess_code[i] == guess_code[j]){

	// Increment n_right
	if (result[j] == RIGHT_PLACE){
	  ++n_right;
	}

	// Increment n_guess
	if (j < i){
	  ++n_guess;
	}

      }

      // How many times does this letter appear in
      // the secret code?
      if (guess_code[i] == secret_code[j]){
	++n_secret;
      }
    }

    // If this is the right guess, then continue
    if (result[i] == RIGHT_PLACE){
      continue;
    }

    // Fill wrong place
    if (n_secret - n_right - n_guess > 0){
      result[i] = WRONG_PLACE;
    } 
  }

  return;
}

