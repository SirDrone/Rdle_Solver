# Rdle_Solver
A prototype Wordle/Absurdle\* Python solver

### This solver can:
- Tackle Wordle (https://www.nytimes.com/games/wordle/index.html)
- Tackle Absurdle (https://qntm.org/files/absurdle/absurdle.html)
- Tackle a custom Wordle

*\*All mentioned games are owned by their respective entities.*

### Requirements to run the solver:
- We'll first need to ensure we have a terminal or CMD environment
- We'll also need Python3 installed
- Next, we'll need to install any required dependencies (e.g. pip)

### Officially running the solver [from the terminal within the correct folder]:
     python3 frontend.py

### How does the solver work you may ask?
- We start with a five-letter wordlist
- Three word-reduction modes are employed:
    - Spread guessing (picking a word with no repeating or previously used letters)
    - Elimination guessing (picking a word that can tactically reduce options)
    - BYG elimination (reduces words based on the respective colors)
- Colors are currently user-supplied through the terminal or command-prompt

### Limitations:
- Indeed, this is but a terminal/command line tool.  The "AI" is also rule-based.  But it is the first phase towards:
    - A computer vision-based program that can self-interact directly with the sites
    - A potential machine-learning program that can optimize the Wordle/Absurdle guess count and pick more beneficial words

### Shoutout to Charles Reid and Donald Knuth for the original wordlist:
- https://github.com/charlesreid1/five-letter-words/blob/master/sgb-words.txt
