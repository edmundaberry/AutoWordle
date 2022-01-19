import numpy as np
cimport numpy as np

cdef extern from "fastwordle.h":
    void c_get_result (np.int32_t* guess_code, np.int32_t* secret_code, np.int32_t* result, long n_letters)

cdef extern from "fastwordle.h":
    void c_get_results (np.int32_t* guess_codes, np.int32_t* secret_code, np.int32_t* results, long n_letters, long n_guesses)

cdef extern from "fastwordle.h":
    double c_get_score (np.int32_t* guess_codes, np.int32_t* secret_code, long n_letters, long n_guesses)

cdef extern from "fastwordle.h":
    double c_get_best_score(np.int32_t* guess_codes, np.int32_t* secret_code, np.int32_t* best_code, long n_letters, long n_guesses, long n_secrets)

def get_result(np.ndarray[np.int32_t, ndim=1] guess_code,
               np.ndarray[np.int32_t, ndim=1] secret_code):

    cdef int n_letters;
    n_letters = int (len(guess_code));

    cdef np.ndarray[np.int32_t, ndim=1] result;
    result = np.zeros((n_letters,), dtype=np.int32)
    c_get_result(<np.int32_t*> guess_code.data,
                 <np.int32_t*> secret_code.data,
	         <np.int32_t*> result.data,
	         n_letters);
    
    return result

def get_results(np.ndarray[np.int32_t, ndim=2] guess_codes,
                np.ndarray[np.int32_t, ndim=1] secret_code):

    cdef int n_guesses, n_letters;
    n_guesses = int(guess_codes.shape[0]);
    n_letters = int(guess_codes.shape[1]);

    cdef np.ndarray[np.int32_t, ndim=2] results;
    results = np.zeros((n_guesses, n_letters), dtype=np.int32)
    c_get_results(<np.int32_t*> guess_codes.data,
                  <np.int32_t*> secret_code.data,
	          <np.int32_t*> results.data,
	          n_letters, n_guesses);
    
    return results

def get_score(np.ndarray[np.int32_t, ndim=2] guess_codes,
              np.ndarray[np.int32_t, ndim=1] secret_code):

    cdef int n_letters, n_guesses;
    n_guesses = int(guess_codes.shape[0]);
    n_letters = int(guess_codes.shape[1]);

    cdef double score;
    score = c_get_score(<np.int32_t*> guess_codes.data,
                        <np.int32_t*> secret_code.data,
    			n_letters,
			n_guesses);
    
    return score

def get_best_score(np.ndarray[np.int32_t, ndim=2] guess_codes,
                   np.ndarray[np.int32_t, ndim=2] secret_codes):


    cdef int n_guesses, n_letters, n_secrets;
    n_guesses = int(guess_codes.shape[0]);
    n_letters = int(guess_codes.shape[1]);
    n_secrets = int(secret_codes.shape[0]);

    cdef np.ndarray[np.int32_t, ndim=1] best_code;
    best_code = np.zeros((n_letters,), dtype=np.int32)

    cdef double best_score;

    best_score = c_get_best_score(<np.int32_t*> guess_codes.data,
                                  <np.int32_t*> secret_codes.data,
				  <np.int32_t*> best_code.data,
				  n_letters,
				  n_guesses,
				  n_secrets);

    return best_code, best_score