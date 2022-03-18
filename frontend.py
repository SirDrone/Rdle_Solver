#!/usr/bin/env python3

import re
from rdle_solver import Rdle_Solver

def start_game():
    #Grab our allowed five-letter words
    with open("custom.txt", 'r') as lst:
        words = [ w.rstrip("\n") for w in lst.readlines() if len(w.rstrip("\n")) == 5 ]

    #Prepare the game
    response = prompt_user_for_game_mode() #Ask user what game mode they would like
    if response in ['O', 'C', 'A']:
        word = None
        if response == 'C': #Custom word challenge; ask the user for a valid word
            word = prompt_user_for_word(words)
        rs = Rdle_Solver(word=word, verbose_level=1)
        game_active = True #If a word is supplied, we'll guess against it, otherwise we'll begin Wordle/Absurdle
        while game_active:
            result = rs.guess_and_evaluate_success()
            if result:
                game_active = False
                print("Yes, we won!")
            elif response != 'A' and rs.get_guess_count() > 5: #If Wordle or a custom game, we only have six guesses to get it right
                game_active = False
                print("Ugh, we lost!")
        print("Final board:") #Either way we'll show the end board
        rs.show_board()

#Ask the user what they would like to do.  O == Wordle, C == Custom word challenge, A == Absurdle
def prompt_user_for_game_mode():
    incorrect_format = True
    response = ""
    while incorrect_format:
        response = input("Official Game (O), Challenge the Solver (C), Absurdle (A), or Exit (E)?\n").upper()
        if len(response) == 1:
            if re.match("[OCAE]{1}", response):
                incorrect_format = False
    return response

#Per the custom-word challenge, ask the user what five-letter word they want us to guess against
def prompt_user_for_word(words):
    incorrect_format = True
    word = None
    while incorrect_format:
        word = input("Please pick a valid five-letter word:\n")
        if word in words:
            incorrect_format = False
    return word

if __name__ == "__main__":
    start_game()
