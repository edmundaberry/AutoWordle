import numpy as np
from string import ascii_uppercase
from fastwordle import get_results, get_result, get_score, get_best_score
import matplotlib.pyplot as plt

RIGHT_PLACE = 1
WRONG_PLACE = 2
NOT_PRESENT = 3
EMPTY       = 4

def get_alphabet():

    # Make the alphabet
    alphabet = np.zeros(26, dtype="O")
    for i, l in enumerate(ascii_uppercase):
        alphabet[i] = l
    
    # Return
    return alphabet

def decode(code, alphabet = None):
    
    # Get alphabet if it's not there
    if alphabet is None:
        alphabet = get_alphabet()
    
    # Get list of letters
    letters = alphabet[code].tolist()
    
    # Combine
    word = "".join(letters)
    
    # Return
    return word

def encode(word, alphabet=None):
    
    # Get alphabet if it's not there
    if alphabet is None:
        alphabet = get_alphabet()

    # Get code
    code = np.searchsorted(a=alphabet, v=list(word))
    code = code.astype(np.int32)
    
    # Return
    return code

def build_dictionary(path, alphabet=None):
    
    # Read the file
    with open(path, "r") as f:
        words = f.read().strip().split("\n")
    
    # Size
    N_cols = 5
    N_rows = len(words)
        
    # Make a word matrix buffer
    word_mat = np.zeros((N_rows, N_cols), dtype=np.int32)
        
    # Fill the word matrix buffer
    for i_word, word in enumerate(words):
        word_mat[i_word,:] = encode(word=word, alphabet=alphabet)

    # Return word matrix buffer
    return words, word_mat

def get_result_slow(guess_code, secret_code):
    
    # Size
    n = len(guess_code)
    
    # Sanity check
    assert (len(secret_code) == n)
    
    # Result buffer
    result = np.zeros(n, dtype=np.int32)
    
    # Default to not present
    result.fill(NOT_PRESENT)
    
    # Do correct loop first
    lit_idx = (guess_code == secret_code)
    result[lit_idx] = RIGHT_PLACE
    
    # Get counts
    unique_letter_guess = np.unique(guess_code)
    
    # Letters that are in the wrong place but in the word
    for l in unique_letter_guess:
                
        # How many to light?
        secret_idx  = (secret_code == l)
        guess_idx   = (guess_code  == l)
        result_l    = result[guess_idx]
        n_to_light  = secret_idx.sum()
        n_lit       = (result_l == RIGHT_PLACE).sum()
        n_to_light -=  n_lit
        
        # Which to light?
        to_light = np.setdiff1d(np.where(guess_idx)[0], np.where(lit_idx)[0])
        to_light = to_light[:n_to_light]
        
        # Light
        result[to_light] = WRONG_PLACE
        
    # Return
    return result

class Constraint(object):
    
    def __init__(self):
        self.known_missing = None
        self.known_present = None
        self.min_counts = None
        self.max_counts = None

def get_row_constraints(guess, result, alphabet=None):
        
    # Size
    n = len(guess)
    if alphabet is None:
        alphabet = get_alphabet()
    N = len(alphabet)
    
    # Get unique guesses
    unique_guess_letters = np.unique(guess)
    
    # Buffers
    known_missing = [None,] * n
    known_present = np.zeros(n, dtype=np.int32)
    min_counts    = np.zeros(N, dtype=np.int32)
    max_counts    = np.zeros(N, dtype=np.int32)

    # Initialize buffers
    known_present.fill(EMPTY)
    min_counts.fill(0)
    max_counts.fill(n)

    # Fill known buffers
    known_idx = (result == RIGHT_PLACE)
    known_present[known_idx] = guess[known_idx]
    
    # Start missing buffer
    for i, l in enumerate(guess):
        if result[i] == WRONG_PLACE:
            if known_missing[i] is None:
                known_missing[i] = set()
            known_missing[i].add(l)
    
    # Fill min and max count buffers and increment missing buffer
    for l in unique_guess_letters:
        
        # How many are unlit?
        idx1 = (guess == l)
        idx = np.where(idx1)[0]
        result_l = result[idx]
        n_unlit = (result_l == NOT_PRESENT).sum()
        
        # How many are lit?
        n_lit = len(idx) - n_unlit
        
        # At minimum, there are `n_lit` instances
        min_counts[l] = n_lit
        
        # If there are any unlit, then there are at most `n_lit` instances
        if n_unlit:
            max_counts[l] = n_lit
            idx2 = (result == NOT_PRESENT)
            idx_missing = np.where(np.logical_and(idx1, idx2))[0]
            for m in idx_missing:
                if known_missing[m] is None:
                    known_missing[m] = set()
                known_missing[m].add(l)
                
    # Constraints object
    c = Constraint()
    c.known_present = known_present
    c.known_missing = known_missing
    c.min_counts = min_counts
    c.max_counts = max_counts
    
    # Return     
    return c

def prune(candidates, constraint, alphabet = None):
    
    # Alphabet
    if alphabet is None:
        alphabet = get_alphabet()
    
    # Prune by known present
    idx = None
    for i, letter in enumerate(constraint.known_present):
        if letter == EMPTY:
            continue
        tmp_idx = (candidates[:,i] == letter)
        idx = tmp_idx if idx is None else np.logical_and(idx, tmp_idx)
    if idx is not None:
        candidates = candidates[idx]

    # Prune by known absent
    idx = None
    for i, missing_letters in enumerate(constraint.known_missing):
        if missing_letters is None:
            continue
        for missing_letter in missing_letters:
            tmp_idx = (candidates[:,i] != missing_letter)
        idx = tmp_idx if idx is None else np.logical_and(idx, tmp_idx)
    if idx is not None:
        candidates = candidates[idx]

    # Prune by counts
    idx = None
    for i in range(len(alphabet)):
    
        count = (candidates == i).sum(axis=1)
        tmp_idx = np.logical_and(count >= constraint.min_counts[i],
                                 count <= constraint.max_counts[i])
    
        idx = tmp_idx if idx is None else np.logical_and(idx, tmp_idx)
    if idx is not None:
        candidates = candidates[idx]

    # Return
    return candidates

class Game(object):
    
    def __init__(self, n_tries = 6, n_letters = 5):
        
        # Build the alphabet
        self._alphabet = get_alphabet()
        
        # Build the dictionary
        self._dictionary, self._all_candidates = build_dictionary(path="data/words_scrape.txt",
                                                                  alphabet=self._alphabet)
        
        # Candidates
        self._candidates = self._all_candidates.copy()
        
        # Store dimensions
        self._n_tries     = n_tries
        self._n_letters   = n_letters
        
        # Buffer for guesses, default to empty
        self._guesses = np.zeros((self._n_tries, self._n_letters), dtype=np.int32)
        self._guesses.fill(EMPTY)
        
        # Buffer for results, default to empty
        self._results = np.zeros((self._n_tries, self._n_letters), dtype=np.int32)
        self._results.fill(EMPTY)
                
        # Trial counter
        self._trial = 0

    def show(self):
    
        # What colors to use?
        color_map = {
            EMPTY      : "white",
            RIGHT_PLACE: "green", 
            WRONG_PLACE: "yellow",
            NOT_PRESENT: "gray"
        }

        # Make the grid and set the size
        fig, axs = plt.subplots(self._n_tries, self._n_letters)
        fig.set_size_inches(self._n_letters, self._n_tries)
    
        # Loop over rows
        for i_row, row in enumerate(axs):
        
            # Does this row have a word?
            word = None
            if i_row < self._trial:
                code = self._guesses[i_row]
                word = decode(code, alphabet=self._alphabet)
        
            # Loop over the columns
            for i_col, ax in enumerate(row):
            
                # No axis markers
                ax.get_xaxis().set_ticks([])
                ax.get_yaxis().set_ticks([])
                    
                # Get the result and color the square accordingly
                result = self._results[i_row, i_col]
                color  = color_map[result]
                ax.set_facecolor(color)
            
                # If we have a word, write the letter
                if word is not None:
                    ax.text(0.5, 0.5, word[i_col],
                        verticalalignment  ='center',
                        horizontalalignment='center',
                        transform=ax.transAxes,
                        color='black',
                        fontsize=30)

    def blacklist_one(self, word):
        
        print("Removing '{}' from the list of candidates".format(word))
        code = encode(word, alphabet=self._alphabet)
        self._candidates = self._candidates[~np.all(self._candidates == code, axis=1)]
        
    def blacklist(self, words):
        
        if isinstance(words, list):
            for w in words:
                self.blacklist_one(w)
        elif isintance(words, str):
            self.blacklist_one(words)
        else:
            raise ValueError("What is this blacklist? {}".format(words))
            
    def print_candidates(self):
        print("Remaining candidates are:")
        for c in self._candidates:
            print("\t{}".format(decode(c)))

    def ask(self):
            
        # Get the best candidate
        best_candidate_code, n_lit_expected = get_best_score(self._candidates, self._candidates)
            
        # Decode the best candidate
        best_candidate_word = decode(best_candidate_code)

        # Report
        print("I think that the best candidate is {}".format(best_candidate_word))
        print("Expect {} lit squares if you guess {}".format(n_lit_expected, best_candidate_word))
        print("Before guessing {}, there are {} remaining candidates".format(best_candidate_word, len(self._candidates)))

        # Return
        return best_candidate_word

    def evaluate(self):
        
        # Get constraint
        constraint = get_row_constraints(self._guesses[self._trial-1],
                                         self._results[self._trial-1])
            
        # Apply constraint
        self._candidates = prune(candidates=self._candidates,
                                 constraint=constraint, 
                                 alphabet = self._alphabet)
        
        # If we won, no need to report more
        if np.all(self._results[self._trial-1] == RIGHT_PLACE):
            return
        
        # If we lost, no need to report more
        if self._trial >= self._n_tries:
            return
            
        # Report
        print("There are now {} remaining candidates".format(len(self._candidates)))
                                                                            
        # If there are few enough additional candidates, print them:
        if len(self._candidates) <= 10:
            self.print_candidates()

class OracleGame(Game):
    
    def __init__(self, secret_word, n_tries = 6, n_letters = 5):
        Game.__init__(self, n_tries=n_tries, n_letters=n_letters)
        
        # Sanity check
        if len(secret_word) != n_letters:
            msg = "Secret word '{}' must have {} letters, not {}"
            msg = msg.format(secret_word, n_letters, len(secret_word))
            raise ValueError(msg)
                    
        # Secret word and its code
        self._secret_word = secret_word
        self._secret_code = encode(self._secret_word, alphabet=self._alphabet)
        
    def guess(self, word):
        
        # Make sure word has correct number of letters
        if len(word) != self._n_letters:
            msg = "'{}' needs to have {} letters, not {}"
            msg = msg.format(word, self._n_letters, len(word))
            print(msg)
            return
        
        # Make sure word is in the dictionary
        if word not in self._dictionary:
            msg = "'{}' is not in the dictionary"
            msg = msg.format(word)
            print(msg)
            return
                
        # Encode
        code = encode(word, alphabet=self._alphabet)
        
        # Store the code in the grid
        self._guesses[self._trial] = code
        
        # Get the result
        self._results[self._trial] = get_result(guess_code=code, secret_code=self._secret_code)
        
        # Increment the trial
        self._trial += 1

        # Winner?
        if np.all(self._results[self._trial-1] == RIGHT_PLACE):
            print("WINNER! SECRET WORD WAS '{}'".format(word))
            return
                
        # Loser?
        if (self._trial >= self._n_tries):
            print ("GAME OVER")
                                

class RealGame(Game):
    def __init__(self, n_tries = 6, n_letters = 5):
        Game.__init__(self, n_tries=n_tries, n_letters=n_letters)

    def guess(self, word, result):
        
        # Make sure word has correct number of letters
        if len(word) != self._n_letters:
            msg = "'{}' needs to have {} letters, not {}"
            msg = msg.format(word, self._n_letters, len(word))
            print(msg)
            return
        
        # Make sure result has correct number of letters
        if len(result) != self._n_letters:
            msg = "'{}' needs to have {} letters, not {}"
            msg = msg.format(result, self._n_letters, len(result))
            print(msg)
            return
                
        # Encode
        code = encode(word, alphabet=self._alphabet)
        
        # Store the code in the grid
        self._guesses[self._trial] = code
        
        # Get the result
        self._results[self._trial] = result
        
        # Increment the trial
        self._trial += 1

        # Winner?
        if np.all(self._results[self._trial-1] == RIGHT_PLACE):
            print("WINNER! SECRET WORD WAS '{}'".format(word))
            return
                
        # Loser?
        if (self._trial >= self._n_tries):
            print ("GAME OVER")
