import typer
import random
import curses
import time
import os
import json
import pyfiglet
from asciimatics.screen import Screen
from intro_animation import intro

VERSION = 1.0
ALL_LANGUAGES = [{"name": "English", "flag": "🇬🇧"}, {"name": "Spanish", "flag": "🇪🇸"}]

DEFAULT_LANGUAGE = "english"
DEFAULT_WORDS = 20
DEFAULT_TIME = 30
DEFAULT_QUOTES = False
#DEFAULT_SOUND = False
DEFAULT_SAVE = False

app = typer.Typer()

def select_random_words(path, count):

	with open(path, "r", encoding="utf-8") as file:
		word_list = file.read().splitlines()

	random_words = random.sample(word_list, count)

	return random_words

def select_random_quote(path):

	with open(path, "r", encoding="utf-8") as file:
		quotes = json.load(file)
	
	random_quote = random.choice(quotes)
	quote_text = random_quote["quote"]
	author = random_quote["author"]
	quote_length = len(quote_text)
	
	return quote_text, author, quote_length

def calculate_wpm(start_time: float, end_time: float, word_count: int) -> float:

	elapsed_time = end_time - start_time
	minutes = elapsed_time / 60 
	wpm = word_count / minutes

	return wpm

def calculate_accuracy(correct_letters: int, total_letters: int) -> float:

	if total_letters == 0:
		return 0.0
	
	accuracy = (correct_letters / total_letters) * 100

	return accuracy

def calculate_stats(text, text_input, start_time, end_time):

	word_count = 0
	correct_letters = 0
	total_letters = len(text)
		
	# all this crap to transform the text
	text_list = text.split()
	joined_text_input = ''.join(text_input)
	words_text_input = joined_text_input.split()

	for original_word, user_word in zip(text_list, words_text_input):
		if original_word == user_word:
			word_count += 1

	wpm = calculate_wpm(start_time, end_time, word_count)
	typer.echo(f"{round(wpm, 1)} WPM")

	for i in range(min(len(text), len(text_input))):
		if text[i] == text_input[i]:
			correct_letters += 1

	accuracy = calculate_accuracy(correct_letters, total_letters)
	typer.echo(f"{round(accuracy)}%")

	return wpm, accuracy

def clear_console():

	if os.name == "posix":
		_ = os.system("clear")
	else:
		_ = os.system("cls")

def display_text(stdscr, target, current, wpm=0):

	stdscr.addstr(target)

	for i, char in enumerate(current):
		correct_char = target[i]
		color = curses.color_pair(1)
		if char != correct_char:
			color = curses.color_pair(2)

		stdscr.addstr(0, i, char, color)
			  
def game(stdscr, text):

	curses.curs_set(0)
	curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) 

	target_text = text
	current_text = []   

	while True:
		stdscr.clear()
		display_text(stdscr, target_text, current_text)
		stdscr.refresh()

		if "".join(current_text) == target_text:
			stdscr.nodelay(False)
			break

		try:
			key = stdscr.getkey()
		except:
			continue

		if ord(key) == 10:
			break

		if key in ("KEY_BACKSPACE", '\b', "\x7f"):
			if len(current_text) > 0:
				current_text.pop()
		elif len(current_text) < len(target_text):
			current_text.append(key)
		else:
			stdscr.clear()
			break

	return current_text

@app.command()
def typy(language: str = typer.Option(DEFAULT_LANGUAGE, "--lang", help="Language to use"),
		 words: int = typer.Option(DEFAULT_WORDS, "--words", help="Number of words"),
		 timer: int = typer.Option(DEFAULT_TIME, "--time", help="Define time (seconds)"),
		 quotes: bool = typer.Option(DEFAULT_QUOTES, "--quotes", help="Select quotes instead of words"),
		 sound: bool = typer.Option(DEFAULT_SAVE, "--save", help="Choose if you want to save your stats")):
	
	if language.lower() not in ["english", "español"]:
		typer.echo("Invalid language! Please choose 'english' or 'español'.")
		raise typer.Abort()

	if quotes:
		text, author, length = select_random_quote(f"quotes/{language}.json")

	else:
		text = select_random_words(f"words/{language[0:2]}-1000", words)
		text = ' '.join(text)

	clear_console()

	Screen.wrapper(intro)

	start_time = time.time()

	text_input = curses.wrapper(game, text)

	end_time = time.time()

	wpm, accuracy = calculate_stats(text, text_input, start_time, end_time)

	# display statistics here

	typer.echo("The game has finished. Press 'q' to quit or 'r' to restart")
	while True:
		key = typer.getchar()
		if key == "q":
			break
		elif key == "r":
			clear_console()
			start_time = time.time()
			text_input = curses.wrapper(game, text)
			end_time = time.time()
			wpm, accuracy = calculate_stats(text, text_input, start_time, end_time)
			typer.echo("The game has finished. Press 'q' to quit or 'r' to restart")
		else:
			typer.echo("Invalid key. Press 'q' to quit or 'r' to restart.")

@app.command()
def help():
	
	clear_console()
	help_text = pyfiglet.figlet_format("HELP", font="slant")

	typer.echo("\n")
	typer.echo(help_text)
	typer.echo(f"Welcome to TyPy, a terminal-based typing game developed with Python.")
	typer.echo("\nUSAGE:")
	typer.echo("  typy.exe [OPTIONS] COMMAND [ARGS]")
	typer.echo("\nOPTIONS:")
	typer.echo("    version                     Check current version of TyPy.")
	typer.echo("    show-languages              Show all the available languages.")
	typer.echo("  --install-completion          Install completion for the current shell.")
	typer.echo("  --show-completion             Show completion for the current shell, to copy it or customize the installation.")
	typer.echo("\nCOMMANDS:")
	typer.echo("  --lang TEXT                   Select the language of the game (e.g., 'english', 'spanish').")
	typer.echo("  --words INTEGER               Define the number of words for the game.")
	typer.echo("  --timer INTEGER               Specify amount of time you want to play.")
	typer.echo("  --quotes BOOL                 Play with quotes instead of words.")
	typer.echo("  --save BOOL                   Choose if you want to save your statistics locally in your computer.")
	typer.echo("\nARGS:")
	typer.echo("  <values>")
	typer.echo("\n")

	time.sleep(1.5)

@app.command()
def version(version : bool = typer.Option(None, "--version", "--v", help="Check current version")):

	clear_console()
	typy_text = pyfiglet.figlet_format(f"TyPy {VERSION}", font="larry3d")

	typer.echo(f"{typy_text}")

	time.sleep(1.5)

@app.command()
def show_languages(show_languages: bool = typer.Option(None, "--show-languages", "--showl", help="Show all the available languages")):

	clear_console()
	typer.echo("╔════════════════════════════════════╗")
	typer.echo("║        Available Languages         ║")
	typer.echo("╚════════════════════════════════════╝")

	for language in ALL_LANGUAGES:
		time.sleep(0.7)
		typer.echo(f"║  {language['flag']} {language['name'].ljust(16)}" + " "*(22 - len(language['name'])) + "║")

	typer.echo(' ' + "═"*36)

if __name__ == "__main__":
	app()