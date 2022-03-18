#!/usr/bin/env python3

import re
from random import choice
from termcolor import colored
from collections import Counter

#Terminal-based prototype class for solving Wordle, Absurdle, etc.
class Rdle_Solver:
    def __init__(self, word=None, verbose_level=0):
        self.__wordlist = "custom.txt"
        with open(self.__wordlist, 'r') as lst:
            self.__original_words = [ w.rstrip("\n") for w in lst.readlines() if len(w.rstrip("\n")) == 5 ]
        self.__words = self.__original_words.copy()
        self.__spread_words = [ w for w in self.__words if len(w) == len(set(w)) ]
        self.__guesses = []
        self.__guess_count = 0
        self.__guess_mode = 1
        self.__positive_letters = []
        self.__positive_positions = []
        self.__colors = []
        self.__answer_word = self.__check_word(word) #The answer to the game can be user-supplied, so we'll check if it's set
        self.__verbose_level = verbose_level if type(verbose_level) == int and (-1 < verbose_level < 3 ) else 0

    #Responsible for making guesses and narrowing options
    def guess_and_evaluate_success(self):
        guess = self.__take_guess()
        result = self.__evaluate_guess(guess)
        self.__guess_count += 1
        return result

    #To visually see the current board
    def show_board(self):
        for i in range(0, len(self.__guesses)):
            guess = self.__guesses[i]
            colors = self.__colors[i]
            colored_guess = ""
            for j in range(0, len(guess)):
                g = guess[j]
                color = colors[j]
                if color == 'g':
                    colored_guess += colored(g, "green")
                elif color == 'y':
                    colored_guess += colored(g, "yellow")
                else:
                    colored_guess += colored(g, "white")
            print(f"[{i+1}]: {colored_guess}")

    def get_guess_count(self):
        return self.__guess_count

    def get_guess_mode(self):
        return self.__guess_mode

    def get_guesses(self):
        return self.__guesses

    def get_colors(self):
        return self.__colors

    #############################################################################
    #                               Helper Functions                            #
    #############################################################################

    #Check if the user-supplied answer is set and valid.  If it isn't set, we'll later help the user guess it
    def __check_word(self, word):
        if word != None and word not in self.__original_words:
            raise ValueError(f"Word ({word}) not found!")
        return word

    #The guessing function.  Facilitates how to guess based on the stage of the game
    def __take_guess(self):
        guess = ""
        if self.__guess_count == 0:
            guess = self.__take_spread_guess()
        else:
            if any([ len(x) >= 4 for x in [self.__positive_letters, self.__positive_positions] ]) \
                    or self.__guess_count >= 5 or len(self.__spread_words) == 0:
                guess = self.__take_final_guess()
            else:
                guess = self.__take_spread_guess()
        return guess

    #Make a guess based purely on words with no repeating letters, nor any letters previously tried
    def __take_spread_guess(self):
        self.__guess_mode = 1
        if self.__verbose_level > 0:
            print("Mode 1: Spread guess")
        guess = choice(self.__spread_words)
        return guess
        
    #Make an educated guess either utilizing heavier strategy or simply picking whatever's left
    def __take_final_guess(self):
        if len(self.__words) == 0:
            raise IndexError("Out of words!  Exiting..")
        do_tactical_elimination = self.__tactical_elimination_is_necessary()
        if do_tactical_elimination: #If we find a rare end-game close call
            self.__guess_mode = 3
            guess = self.__perform_tactical_elimination()
        else: #Otherwise, we can just pick a word from our standard byg elimination
            self.__guess_mode = 2
            if self.__verbose_level > 0:
                print("Mode 2: Educated guess")
            guess = choice(self.__words)
        return guess

    #Supports the final guess function in determing if a smarter strategy is needed for end-game elimination
    def __tactical_elimination_is_necessary(self):
        enter_tactical_elimination = False
        if ((2 < len(self.__words) < 7) and (self.__guess_count < 5)):
            combined_phrase = ''.join(map(str, self.__words))
            trick_letters = [ k for k,v in Counter(combined_phrase).items() if v == 1 ]
            diff = len(trick_letters) - len(self.__words)
            if diff in [-1, 0, 1]:
                enter_tactical_elimination = True
            if self.__positive_positions == 4:
                enter_tactical_elimination = True
        return enter_tactical_elimination

    #A special elimination mode for detected endgame close-calls like [fease, cease, pease]
    #It will pick the word with the most spread.  From the above example, "pacer" would greatly reduce options
    def __perform_tactical_elimination(self):
        if self.__verbose_level > 0:
            print("Mode 3: Tactical elimination")
        trick_letters = [ k for k,v in Counter(''.join(map(str, self.__words))).items() if v == 1 ]
        get_favorability = lambda w: sum([ t in w for t in trick_letters ])
        favorability_map = {}
        [ favorability_map.update({w:get_favorability(w)}) for w in self.__original_words ]
        guess = sorted(favorability_map, key=lambda x: favorability_map[x]*-1)[0] #Pick a word to help eliminate choices
        return guess

    #Determine how our guess fared and make adjustments
    def __evaluate_guess(self, guess):
        colors = ""
        if self.__answer_word == None: #An official Wordle or Absurdle session
            [guess, colors] = self.__get_user_feedback(guess)
        else: #The user supplied us a fixed word that we have to guess and can self-adjust colors against
            colors = self.__get_auto_feedback(guess)
        colors = self.__recolor(guess, colors)
        self.__guesses.append(guess)
        self.__colors.append(colors)
        if colors == "ggggg":
            return True
        if self.__guess_mode == 1: #Reduce possible spread words
            self.__spread_words = [ w for w in self.__spread_words if not any([c in w for c in guess ]) ] 
        self.__perform_byg_elimination(guess, colors)
        return False

    #If we're assisting the user against Wordle or Absurdle, we'll need their feedback to know how we're doing
    def __get_user_feedback(self, guess):
        incorrect_format = True
        colors = ""
        while incorrect_format:
            colors = input(f"Guess #{self.__guess_count + 1}: {guess}\nHow did we do?  " \
                    "Colors are black (b), yellow (y), green (g)\nWe can also remove the word (r) " \
                    "if the word can't be entered\nLastly, you can forsake our recommendation and " \
                    "enter a custom one (c)\nInput 5 characters representing colors (e.g. bbygb), or enter 'r' or 'c':\n")
            if len(colors) == 5:
                if re.match("[byg]{5}", colors):
                    incorrect_format = False
            elif len(colors) == 1:
                if re.match("[r]{1}", colors): #Remove the guessed word from our lists and the source file
                    for lst in [self.__original_words, self.__words, self.__spread_words]:
                        while guess in lst:
                            lst.remove(guess)
                    with open(self.__wordlist, 'w') as lst:
                        lst.write(''.join(map(str, [ f"{w}\n" for w in self.__original_words ])))
                    if self.__verbose_level > 0:
                        print(f"Word [{guess}] permanently removed.")
                    guess = self.__take_guess()
                elif re.match("[c]{1}", colors): #Allow the user to provide a custom guess
                    custom_guess = input("Please pick a valid five-letter word:\n")
                    if custom_guess in self.__original_words and custom_guess not in self.__guesses:
                        guess = custom_guess
        return [guess, colors]

    #If the user gave us a word to have us guess against it, we can auto-assign colors based on our performance
    def __get_auto_feedback(self, guess):
        colors = ""
        for i in range(0, len(guess)):
            g = guess[i]
            w = self.__answer_word[i]
            if g == w:
                colors += 'g'
            elif g in self.__answer_word:
                colors += 'y'
            else:
                colors += 'b'
        if self.__verbose_level > 0:
            print(f"{guess} | {colors}")
        return colors

    #Recolor in case something like "beefy" is seen as "ygbbb", when it should be "ygybb"
    def __recolor(self, guess, colors):
        color_map = {}
        for i in range(0, len(guess)):
            g = guess[i]
            c = colors[i]
            mapped_color = color_map.get(g)
            if mapped_color != None:
                if mapped_color == 'b' and c != 'b':
                    color_map.update({g:c})
            else:
                color_map.update({g:c})
        return ''.join(map(str, [ 'y' if (color_map.get(guess[i]) != 'b' and colors[i] == 'b') \
                else colors[i] for i in range(0, len(guess)) ]))

    #This is the standard elimination model.
    #Basically, if we have a 'b' as the color for a given letter, we know it isn't in any of the possible words at all
    #If we have a 'y', we know it isn't in the current letter position for any of our words, but it must be in our words
    #Lastly, if we have a 'g', we know the letter must be in that precise position for our words
    def __perform_byg_elimination(self, guess, colors):
        index = 0
        while index < len(guess):
            guess_char = guess[index]
            color_char = colors[index]
            if color_char == 'b':
                self.__words = [ w for w in self.__words if guess_char not in w ]
            elif color_char == 'y':
                if guess_char not in self.__positive_letters:
                    self.__positive_letters.append(guess_char)
                self.__words = [ w for w in self.__words if guess_char in w and guess_char != w[index] ]
            elif color_char == 'g':
                if index not in self.__positive_positions:
                    self.__positive_positions.append(index)
                self.__words = [ w for w in self.__words if guess_char == w[index] ]
                if guess_char not in self.__positive_letters:
                    self.__positive_letters.append(guess_char)
            if self.__verbose_level > 1 and self.__guess_count > 2:
                print(f"New words after {color_char}-type elimination of {guess_char}: \n{self.__words}")
            index += 1
