# Wordly

Wordly is a terminal word-guessing game. Guess the hidden word in a limited number of tries and use the feedback symbols to work out the answer.

## Requirements

- Python 3.10 or newer
- The packages listed in `requirements.txt`

## Setup

1. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with the game configuration:

   ```dotenv
   SECRETS_FILE=./secrets.txt
   WORD_LENGTH=5
   WORD_COUNT=100
   MAX_GUESSES=6
   HISTORY_FILE=./history.json
   ```

   Paths are relative to the directory where you launch the game. You can use absolute paths instead.

3. Start the game from the project root:

   ```bash
   python wordle.py
   ```

4. At the menu, run `load_secrets` to generate words for the configured word length before starting your first game.

## How to play

Run `new_game`, then enter guesses of the configured length. Feedback uses:

- Green: correct letter in the correct position
- Yellow: letter is in the word but in a different position
- Black: letter is not in the word

During a game, these commands are available instead of a guess:

- `status` — show guesses used and remaining
- `give_up` — end the game as aborted and reveal the secret
- `back` — return to the menu and save the game as unfinished

## Menu commands

| Command | Description |
| --- | --- |
| `help` | List menu commands |
| `new_game` | Start a game |
| `load_secrets` | Generate and save secret words |
| `view_history` | Display saved games |
| `stats` | Show games played, wins, losses, win rate, and average guesses |
| `reset_stats` | Clear saved history after confirmation |
| `rules` | Display the rules |
| `clear` | Clear the terminal |
| `quit` | Exit Wordly |

Game history is stored as JSON at the path configured by `HISTORY_FILE`.

## Tests

Run the test suite from the project root:

```bash
python -m unittest discover -s tests
```
