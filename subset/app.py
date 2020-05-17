#!/usr/bin/env python3

import random
import re
import math
import os
import time
import sys
import textwrap
import shutil
from pathlib import Path

import colorama


# Style globals
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DEFAULT = "\033[0m"

# Display globals
WIDTH = shutil.get_terminal_size().columns # Falls back to 80
MID_WIDTH = 35

# Filesystem globals
ROOT = os.path.dirname(os.path.abspath(__file__)) 
LOCAL = os.path.join(str(Path.home()), ".subset")

# For the specific game
SEED = round(time.time())


def main():
    global WIDTH
    global SEED

    # On Windows, this allows use of ANSI escape sequences
    colorama.init()

    # Ensure local directory exists
    if not os.path.exists(LOCAL):
        os.makedirs(LOCAL)

    # Load dictionary, this should remove proper nouns and non-alpha words
    with open(os.path.join(ROOT, "dictionary.txt"), encoding="ISO-8859-1") as f:
        dictionary = [line.strip() for line in f.readlines() if 
                set("-_'.?!():;#\"1234567890").isdisjoint(set(line)) and
                not line[0].isupper()]


    # Check for a savefile and load it. This works by setting the random seed
    # and loading all found words. Setup welcome messages
    try:
        # Savefile structure is:
        # #seed
        # {the seed}
        # #found
        # {line}
        # {dilineated}
        # {words}
        #
        # This format is cool because you can just iterate over it using a state
        # machine where any state can transition to any other state

        with open(os.path.join(LOCAL, "savefile.txt")) as f:
            found = []
            state = ""
            for line in f.readlines():
                if line[0] == "#":
                    state = line[1:].strip()
                elif state == "seed":
                    SEED = int(line.strip())
                elif state == "found":
                    if line.strip() != "":
                        found.append(line.strip())
            print_banner()
            message = f"{CYAN}Found save file{DEFAULT}"
    except FileNotFoundError:
        # SEED is already set
        found = []        
        message = f"{BOLD}Welcome to Subset!{DEFAULT} {CYAN}Started a new game{DEFAULT}"


    # Seed it with either the default unixtime, or the seed loaded from the file
    random.seed(SEED)

    # In case it ever comes up, only use operations when restoring state from
    # SEED that have a defined and guaranteed order. Earlier I used letters =
    # list(set(pangram)), then used random.choice(letters). This broke because set
    # does not have a consistent order when converting to a list

    # First make a list of any possible pangram, then pick one
    possible_pangrams = [word for word in dictionary if len(set(word)) == 7]
    pangram = random.choice(possible_pangrams)

    # Pick a special letter, and make a persistent ordered list of the others
    letters = list(set(pangram))
    letters.sort()
    special_letter = random.choice(letters)
    ring_letters = [letter.upper() for letter in letters if not letter is
            special_letter]
    random.shuffle(ring_letters)

    # Make a list of all valid words. The dictionary never needs to be touched
    # again after this
    valid_words = [word for word in dictionary if
            set(word).issubset(set(letters)) and 
            len(word) >= 4 and
            special_letter in word]

    # Quickly find other pangrams that share letters with the starting one
    # (there usually are a few)
    pangrams = [word for word in valid_words if len(set(word)) == 7]


    # Compute both total possible score and score so far (nonzero when loading
    # from a save)
    total_score = sum([score_word(word) for word in valid_words])
    score = sum([score_word(word) for word in found])

    while True:
        # Refresh size every loop
        WIDTH = shutil.get_terminal_size().columns
        clear()
        print_banner()

        # Render game stats to the right of the logo
        score_color = color_score(score, total_score)
        # Save the cursor, not necessary, but nice because we're going to jump
        # back into the logo lines and print score, words, and total pangrams
        print("\033[s")
        print(f"\033[3;{WIDTH-16}H", end="")
        print(align(f"Score: {score_color}{score}{DEFAULT}/{GREEN}{total_score}{DEFAULT}", 16, "r")) 
        print(f"\033[4;{WIDTH-16}H", end="")
        print(align(f"Words: {score_color}{len(found)}{DEFAULT}/{GREEN}{len(valid_words)}{DEFAULT}", 16, "r"))
        print(f"\033[5;{WIDTH-16}H", end="")
        print(align(f"{YELLOW}{pluralize(len(pangrams), 'Pangram')}{DEFAULT}", 16, "r"))
        # Restore the cursor (to one line below the banner separator (===))
        print("\033[u")

        # Print a hexagon of letters, with the common letter in the centre
        print(align(f" {ring_letters[0]} {ring_letters[1]} ", WIDTH, "c"))
        print(align(f"{ring_letters[2]} {YELLOW}{special_letter.upper()}{DEFAULT} {ring_letters[3]}", WIDTH, "c"))
        print(align(f" {ring_letters[4]} {ring_letters[5]} ", WIDTH, "c"))

        # Print out the status message (often the result of last command or
        # guess). Clear it immediately (so just pressing enter can banish it)
        print(message)
        message = ""

        # Collect input in yellow
        print(f"Type word or {BOLD}h{DEFAULT} for help")
        guess = input(f"> {YELLOW}").strip().lower()
        print(DEFAULT, end="")

        # All options should clear the screen (though all should redraw the
        # banner too

        WIDTH = shutil.get_terminal_size().columns
        clear()

        # Ignore empty input
        if guess == "":
            continue

        # About game text, rules/sources
        elif guess == "a":
            print_about()
            pause()

        # Save and exit. This is different from quit because quit shows you your
        # score and deletes your save file
        elif guess == "e":
            print_saveandexit(found)

        # Help text
        elif guess == "h":
            print_help()
            pause()

        # List words out
        elif guess == "l":
            print_foundlist(found, valid_words, score, total_score) 
            pause()

        # Randomize the non-common letter positions
        elif guess == "s":
            random.shuffle(ring_letters)
            message = f"{CYAN}Shuffled{DEFAULT}"

        # Abandon game. This isn't a function because it does a lot of stuff
        elif guess == "q":
            print_quit(found, valid_words, score, total_score) 

        # Tell user when they already used a word
        elif guess in found:
            message = f"{YELLOW}Already played {guess}{DEFAULT}"

        # Anything else must be an untried guess
        else:
            if guess in valid_words:
                # Duplicating the scoring code because we're checking for
                # pangrams too
                if len(guess) == 4:
                    d_score = 1
                else:
                    d_score = len(guess)
                if len(set(guess)) == 7:
                    d_score = d_score + 14
                    message = f"{GREEN}Pangram found! +{pluralize(d_score, 'point')}{DEFAULT}"
                else:
                    message = f"{GREEN}Correct! +{pluralize(d_score, 'point')}{DEFAULT}"
                score = score + d_score
                found.append(guess)

            # An invalid word was inputted. Find out why
            else:
                # May use letters, but missing the common one
                if not special_letter in guess:
                    message = f"{RED}'{guess.title()}' does not contain {YELLOW}{special_letter.upper()}{DEFAULT}"
                # If it is a dictionary word, it must use bad letters
                elif guess in dictionary:
                    message = f"{RED}'{guess.title()}' uses other letters{DEFAULT}"
                # Anything else means the dictionary doesn't have it
                else:
                    message = f"{RED}'{guess.title()}' is not in dictionary{DEFAULT}"
        print() 

def print_banner():
    if WIDTH > 70:
        alignment = "c"
    elif WIDTH > 50:
        alignment = "l"
    else:
        print(f"\n\n\n\n{YELLOW}Subset{DEFAULT}\n"+"="*WIDTH+"\n")
        return

    print(YELLOW, end="")
    print(align("   _____       __              __ ", WIDTH, alignment))
    print(align("  / ___/__  __/ /_  ________  / /_", WIDTH, alignment))
    print(align("  \\__ \\/ / / / __ \\/ ___/ _ \\/ __/", WIDTH, alignment))
    print(align(" ___/ / /_/ / /_/ (__  )  __/ /_  ", WIDTH, alignment))
    print(align("/____/\\__,_/_.___/____/\\___/\\__/  ", WIDTH, alignment))
    print(DEFAULT, end="")
    print()
    print("="*WIDTH)
    print()


def print_foundlist(found, valid_words, score, total_score):
    score_color = color_score(score, total_score)
    print_banner()
    print(f"Found {score_color}{len(found)}{DEFAULT}/{GREEN}{len(valid_words)}{DEFAULT} words:")
    longest = 0
    for word in found:
        if len(word) > longest:
            longest = len(word)

        col_width = longest + 1
        columns = math.floor(WIDTH/col_width)
    for i in range(0, len(found)):
        ending = ""
        if (i+1) % columns == 0:
            ending = "\n"
        if len(set(remove_ansi(found[i]))) == 7:
            print(align(f" {YELLOW}*{DEFAULT}{found[i]}", col_width, "l"), end=ending)
        else:
            print(align(f"  {found[i]}", col_width, "l"), end=ending)
    print()

def print_help():
    print_banner()
    print(align("Commands", WIDTH, "c"))
    print(align("-"*MID_WIDTH, WIDTH, "c"))
    print(align(align("a About this game", MID_WIDTH, "l"), WIDTH, "c"))
    print(align(align("e Save and exit", MID_WIDTH, "l"), WIDTH, "c"))
    print(align(align("h Help (this text)", MID_WIDTH, "l"), WIDTH, "c"))
    print(align(align("l List found words", MID_WIDTH, "l"), WIDTH, "c"))
    print(align(align("q Quit and show words", MID_WIDTH, "l"), WIDTH, "c"))
    print(align(align("s Shuffle letters", MID_WIDTH, "l"), WIDTH, "c"))
    print()

def print_about():
    print_banner()
    print(align("About Subset", WIDTH, "c"))
    print(      align("----------------------------------", WIDTH, "c"))
    print(align(align(f"{YELLOW}Subset{DEFAULT} is a word-finding game.", 35, "l"), WIDTH, "c"))
    print(align(align("Every game, you are presented", 35, "l"), WIDTH, "c"))
    print(align(align("with seven letters, the goal is", 35, "l"), WIDTH, "c"))
    print(align(align("to make as many words as you can", 35, "l"), WIDTH, "c"))
    print(align(align("using those letters. You may use", 35, "l"), WIDTH, "c"))
    print(align(align("the same letter more than once", 35, "l"), WIDTH, "c"))
    print(align(align("in a word. You MUST use the center", 35, "l"), WIDTH, "c"))
    print(align(align("letter in every word. Longer words", 35, "l"), WIDTH, "c"))
    print(align(align("are worth more points. Words that", 35, "l"), WIDTH, "c"))
    print(align(align("use all seven letters are called", 35, "l"), WIDTH, "c"))
    print(align(align("'pangrams' and are worth extra", 35, "l"), WIDTH, "c"))
    print(align(align("points as well.", 35, "l"), WIDTH, "c"))
    print()
    print(align(f"The dictionary is taken from the excellent SCOWL project.", WIDTH, "c"))
    print(align(f"See {ROOT}/DICTIONARY_LICENSE.txt for license information.", WIDTH, "c"))
    print()
    print(align(f"{YELLOW}Subset{DEFAULT} is open source and available at:", WIDTH, "c"))
    print(align(f"{CYAN}https://github.com/rightbrace/subset-game.git{DEFAULT}", WIDTH, "c"))
    print()


def print_quit(found, valid_words, score, total_score):
    print_banner()

    # Double check with the player
    choice = input(align("Really end this game and see results? (y/n) ", WIDTH, "c", end=False))
    if choice.lower() != "y":
        return

    clear()
    print_banner()

    # Resummarize results in middle of page
    score_color = color_score(score, total_score)
    print(align(f"Final score: {score_color}{score}{DEFAULT}/{GREEN}{total_score}{DEFAULT}", WIDTH, "c"))
    print(align(f"Found {score_color}{len(found)}{DEFAULT}/{GREEN}{len(valid_words)}{DEFAULT} words", WIDTH, "c"))

    # Print the words in column, wound words in green and asterecies next to pangrams
    print_words = input(align("Print words? (y/n) ", WIDTH, "c", end=False))
    if print_words.lower() == "y":
        # Colour words that were found and find the maximum sized word
        to_print = []
        longest = 0
        for word in valid_words:
            if word in found:
                out = f"{GREEN}{word}{DEFAULT}"
            else:
                out = word
            to_print.append(out)
            if len(word) > longest:
                longest = len(word)
        
        # Work out how many columns can fit
        col_width = longest + 2
        columns = math.floor(WIDTH/col_width)

        # Spacer
        print()
        print("="*WIDTH)

        # Print words from list (they've been colored, but not starred), placing
        # newlines when appropriate
        for i in range(0, len(to_print)):
            ending = ""
            if (i+1) % columns == 0:
                ending = "\n"
            if len(set(remove_ansi(to_print[i]))) == 7:
                print(align(f" {YELLOW}*{DEFAULT}{to_print[i]}", col_width, "l"), end=ending)
            else:
                print(align(f"  {to_print[i]}", col_width, "l"), end=ending)

        print()
        print("="*WIDTH)
        print(align(f"Pangrams are marked with {YELLOW}*{DEFAULT}", WIDTH, "r"))
        print()

    # Delete savefile
    try:
        os.remove(os.path.join(LOCAL, "savefile.txt"))
    except FileNotFoundError:
        pass

    # Give user a bit of feedback before exiting
    pause()
    sys.exit()


def print_saveandexit(found):
    print_banner()
    really = input(align("Really save and exit? (y/n) ", WIDTH, "c", end=False))

    # Anything other than a y should return the user to safety
    if really[0].lower() != "y":
        return

    save_game(found)
    clear()
    print_banner()
    print(align("Game saved!", WIDTH, "c"))
    print()
    pause()
    sys.exit()

# Some utilities:
def clear():
    print("\033c", end="")

def remove_ansi(string):
    return re.sub("\033\[\d+m", "", string)

def align(string, width, just, end=True):
    strlen = len(remove_ansi(string))
    if just == "l":
        if end:
            return string + " "*(width-strlen)
        else:
            return string
    elif just == "r":
        return " "*(width-strlen) + string
    elif just == "c":
        if end:
            return " "*math.ceil((width-strlen)/2) + string + " "*math.floor((width-strlen)/2)
        else:
            return " "*math.ceil((width-strlen)/2) + string

def pluralize(count, string, plural=""):
    if count == 1:
        return f"1 {string}"
    else:
        if plural =="":
            return f"{count} {string}s"
        else:
            return f"{count} {plural}"

def color_score(score, total_score):
    ratio = score / total_score
    if ratio < 0.33:
        score_color = RED
    elif ratio < 0.66:
        score_color = YELLOW
    else:
        score_color = GREEN
    return score_color

def score_word(word):
    score = 0
    if len(word) == 4:
        score = score + 1
    else:
       score = score + len(word)
    if len(set(word)) == 7:
        score = score + 14
    return score 

def pause():
    input(align(align("[Press Enter]", MID_WIDTH, "l", end=False), WIDTH, "c", end=False))

def save_game(found):
    with open(os.path.join(LOCAL, "savefile.txt"), "w") as f:
        f.write("#seed\n")
        f.write(str(SEED) + "\n")
        f.write("#found\n")
        for word in found:
            f.write(word + "\n")

if __name__ == "__main__":
    main()
