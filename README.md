# Introduction

Subset is an in-CLI word guessing game about finding pangrams. A pangram is a
word or phrase that uses every letter from a given (and in this case limited)
alphabet (as in a set of letters, not as in A-Z).

# Installation

Subset requires Python 3.5 onwards and uses the `colorama` package. 


Platform  |  Compatability
----------|---------------
Linux     | Yes, confirmed
Termux (Android)    | Yes, confirmed
macOS     | Likely, unconfirmed
Windows   | Possibly, unconfirmed

If anyone does run this through macOS or Windows, open an issue if anything is
broken.

## Through Pip

Just run `sudo pip install subset`. Then run `subset` in a terminal.

## From Source

 1. Clone this repository
 2. `cd subset-game`
 3. `pip install .`
 4. `subset`

## Sans-Installation

 1. Clone this repository
 2. `cd subset-game/subset/`
 3. `python app.py`


# The Rules

Each game, the player is given seven letters. One letter is highlighted. The
player must find as many words as they can that use some or all of the letters.
The restrictions are:

- The word must be four or more letters long
- The highlighted letter must be used in every word
- The words are never proper nouns

Not all the letters need to be used per word, and letters can be reused within a
word. If the player inputs a word that uses _every_ letter, it is called a
'pangram' and is worth extra points.

Do not expect to get a perfect score without cheating! The puzzles are
randomly generated and I've seen some pangrams with over a thousand
related words.

# Features & Roadmap

So far I have implemented:

- The basic game as described above
- A savefile stored in `~/.subset`
- Dynamic terminal sizing (experimental)

Features I may add:

- Multiple savefiles at once
- Difficulty selection (this is tricky because its very difficult to qualitatively
  analyze the difficulty of a puzzle. Puzzles with fewer words are harder to
  score on, but easier to get a higher fraction of the total score, and so on)
- Dictionary selection (right now, if you find the dictionary file in your
  Python modules folder, or if you are running straight from the cloned folder,
  you can replace `dictionary.txt` with your own file and the game will run just
  fine, but be aware that it throws out capitalized words and words containing
  anything other than letters)
- Colourschemes

# The Dictionary

The game uses the [SCOWL](http://wordlist.aspell.net/) English words dictionary
sections 10 though 70. Licenses for the wordlists can be found in
`DICTIONARY_LICENSE`.

# License

This software is licensed under the MIT license, the text of which can be found
in the `LICENCE` file.

