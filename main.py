
import os, sys
import numpy as np
import pandas as pd


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
)
SHORT_WORD_LIST_FILE = os.path.join(DATA_DIR, "possible_words.txt")
LONG_WORD_LIST_FILE = os.path.join(DATA_DIR, "allowed_words.txt")


def make_pattern(pattern, guess):
    guess_letters = [x for x in guess]
    return list(zip(guess_letters, pattern))

def guess_word(guess, solution):
    solution_set = set(solution)
    res = []
    for idx in range(5):
        letter = guess[idx]
        correct = letter == solution[idx]
        if correct:
            res.append(1)
        else:
            res.append(-1 if letter not in solution_set else 0)
    return list(zip(guess, res))

def get_word_matrix(file):
    df = pd.read_csv(file, header = None, names = ["word"])
    df["1"] = df.word.str[0]
    df["2"] = df.word.str[1]
    df["3"] = df.word.str[2]
    df["4"] = df.word.str[3]
    df["5"] = df.word.str[4]
    del df["word"]
    return df

def get_possibilities(options, pattern):
    cols = list(range(5))
    for col in cols:
        other_cols = [x for x in cols if x != col]
        letter = pattern[col][0]
        score = pattern[col][1]
        if score == 1:
            options = options[options.iloc[:, col] == letter]
        elif score == 0:
            options = options[(options.iloc[:, col] != letter) & (options.iloc[:, other_cols].isin([letter]).any(axis=1))]
        else:
            options = options[~options.iloc[:, cols].isin([letter]).any(axis=1)]
    return options

def get_number_of_possibilities(options, pattern):
    return len(get_possibilities(options, pattern))

def find_best_guesses(options):
    options['#'] = None
    for x in range(len(options)):
        option = options.iloc[x,:5].values
        option_distribution = []
        for y in range(len(options)):
            pattern = guess_word(option, options.iloc[y,:5].values)
            option_distribution.append(get_number_of_possibilities(options, pattern))

        options.iloc[x, 5] = np.mean(option_distribution)
    return options.sort_values('#').head(10)

def start_game():
    print("Starting a new game...")
    options = get_word_matrix(SHORT_WORD_LIST_FILE)

    input_guess = "slate"
    print(f"Use first guess: {input_guess}")

    while True:
        input_pattern = input("Please enter a five-digit pattern (1: Green | 0: Yellow | -1: Gray): ").split(" ")
        if sum(input_pattern) == 5:
            print("Success!!!")
            sys.exit()
        
        pattern = make_pattern([int(x) for x in input_pattern], input_guess)

        print("Finding best guesses..." )
        options = get_possibilities(options, pattern)
        print("Use one of the following ten guesses: ")
        best_guesses = find_best_guesses(options)
        print(best_guesses)

        input_guess = input("Make a new guess: ")


if __name__ == "__main__":
    start_game()
