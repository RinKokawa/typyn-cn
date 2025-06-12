import typer
import random
import curses
import time
import os
import json
import pkg_resources
import toml
import pyfiglet
import asciichartpy
from asciimatics.screen import Screen
from typyn.resources.intro_animation import intro

VERSION = '1.0.17'
ALL_LANGUAGES = [
    {"name": "中文", "flag": "🇨🇳", "code": "chinese"},
    {"name": "English", "flag": "🇬🇧", "code": "english"},
    {"name": "Spanish", "flag": "🇪🇸", "code": "español"}
]

DEFAULT_LANGUAGE = 'chinese'
DEFAULT_WORDS = 15
DEFAULT_TIME = 40
DEFAULT_QUOTES = False
DEFAULT_SAVE = True

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
	current_streak = 0
	max_streak = 0
		
	# all this crap to transform the text
	text_list = text.split()
	joined_text_input = ''.join(text_input)
	words_text_input = joined_text_input.split()

	for original_word, user_word in zip(text_list, words_text_input):
		if original_word == user_word:
			word_count += 1

	wpm = calculate_wpm(start_time, end_time, word_count)

	for i in range(min(len(text), len(text_input))):
		if text[i] == text_input[i]:
			correct_letters += 1
			current_streak += 1
			if current_streak > max_streak:
				max_streak = current_streak
		else:
			current_streak = 0

	accuracy = calculate_accuracy(correct_letters, total_letters)
	incorrect_letters = total_letters - correct_letters

	return wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak

def clear_console():

	if os.name == "posix":
		_ = os.system("clear")
	else:
		_ = os.system("cls")

def display_text(stdscr, target, current, wpm=0):

	max_y, max_x = stdscr.getmaxyx()
	try:
		# 分页显示或截断处理
		display_target = target[:max_x-1]
		stdscr.addstr(display_target)
		
		for i, char in enumerate(current):
			if i >= max_x-1:
				break
			correct_char = target[i]
			color = curses.color_pair(1)
			if char != correct_char:
				color = curses.color_pair(2)
			stdscr.addstr(0, i, char, color)
	except curses.error:
		pass  # 忽略curses相关错误

def save_game_data(wpm, accuracy):

	if DEFAULT_SAVE:
		local_time = time.localtime()
	
		game_data = {
			"timestamp": time.strftime("%Y-%m-%d %H:%M:%S", local_time),
			"wpm": wpm,
			"accuracy": accuracy
		}

		user_path = pkg_resources.resource_filename(__name__, f"user_data/player_data.json") 
		with open(user_path, 'a') as json_file:
			json.dump(game_data, json_file)
			json_file.write('\n')

def print_game_statistics(wpm, accuracy, total_chars, correct_chars, incorrect_chars, max_streak, language="chinese"):
    if language == "chinese":
        title = pyfiglet.figlet_format("游戏统计")
        print(title)
        time.sleep(0.4)
        print("-" * 56)
        time.sleep(0.4)
        print("每分钟字数:        {:<10}".format(round(wpm, 1)))
        time.sleep(0.2)
        print("准确率:            {:<3}%".format(round(accuracy, 1)))
        time.sleep(0.2)
        print("总字符数:          {:<10}".format(total_chars))
        time.sleep(0.2)
        print("正确字符数:        {:<10}".format(correct_chars))
        time.sleep(0.2)
        print("错误字符数:        {:<10}".format(incorrect_chars))
        time.sleep(0.2)
        print("最大连击:          {:<10}".format(max_streak))
    else:
        title = pyfiglet.figlet_format("Game Statistics")
        print(title)
        time.sleep(0.4)
        print("-" * 56)
        time.sleep(0.4)
        print("WPM:                {:<10}".format(round(wpm, 1)))
        time.sleep(0.2)
        print("Accuracy:           {:<3}%".format(round(accuracy, 1)))
        time.sleep(0.2)
        print("Total Char:         {:<10}".format(total_chars))
        time.sleep(0.2)
        print("Correct Char:       {:<10}".format(correct_chars))
        time.sleep(0.2)
        print("Incorrect Char:     {:<10}".format(incorrect_chars))
        time.sleep(0.2)
        print("Max Streak:         {:<10}".format(max_streak))

    time.sleep(0.4)
    print("-" * 56)

def plot_statistics(language="chinese"):
    timestamps = []
    wpms = []
    accuracies = []

    user_path = pkg_resources.resource_filename(__name__, f"user_data/player_data.json") 

    with open(user_path, 'r') as json_file:
        for line in json_file:
            game_data = json.loads(line)
            timestamps.append(game_data["timestamp"])
            wpms.append(game_data["wpm"])
            accuracies.append(game_data["accuracy"])

    time.sleep(0.7)        

    if language == "chinese":
        print("\n每分钟字数 (历史数据):")
        print(asciichartpy.plot(wpms, {'height': 10}))
        time.sleep(0.7)
        print("\n准确率 (历史数据):")
    else:
        print("\nWPM (historical data):")
        print(asciichartpy.plot(wpms, {'height': 10}))
        time.sleep(0.7)
        print("\nAccuracy (historical data):")
    
    print(asciichartpy.plot(accuracies, {'height': 10}))    
    print("-" * 56)

def game(stdscr, text, language="chinese"):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) 

    target_text = text
    current_text = []

    start_time = time.time()

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

def select_language():
    clear_console()
    print("请选择语言 / Please select language:")
    print("╔════════════════════════════════════╗")
    print("║           选择语言                 ║")
    print("╚════════════════════════════════════╝")
    
    for i, lang in enumerate(ALL_LANGUAGES, 1):
        print(f"{i}. {lang['flag']} {lang['name']}")
    
    while True:
        try:
            choice = int(input("\n请输入选项编号 / Enter option number: "))
            if 1 <= choice <= len(ALL_LANGUAGES):
                return ALL_LANGUAGES[choice-1]['code']
            print("无效选项，请重试 / Invalid option, please try again")
        except ValueError:
            print("请输入数字 / Please enter a number")

@app.command()
def run(language: str = typer.Option(None, "--lang", help="Language to use"),
        words: int = typer.Option(DEFAULT_WORDS, "--words", help="Number of words"),
        timer: int = typer.Option(DEFAULT_TIME, "--time", help="Define time (seconds)"),
        quotes: bool = typer.Option(DEFAULT_QUOTES, "--quotes", help="Select quotes instead of words"),
        save: bool = typer.Option(DEFAULT_SAVE, "--save", help="Choose if you want to save your stats")):
    
    # 如果没有指定语言，则进行交互式选择
    if language is None:
        language = select_language()
    
    if language.lower() not in [lang["code"] for lang in ALL_LANGUAGES]:
        typer.echo("无效的语言选择！/ Invalid language selection!")
        raise typer.Abort()
    
    # 修改文本加载逻辑
    if language.lower() == "chinese":
        try:
            data_path = pkg_resources.resource_filename(__name__, f"data/chinese/long-sentences.json")
            with open(data_path, "r", encoding="utf-8") as f:
                text_data = json.load(f)
                text = random.choice(text_data["content"])  # 随机选择一条长难句
        except Exception as e:
            typer.echo(f"加载中文文本时出错: {str(e)}")
            raise typer.Abort()
    else:
        if quotes:
            data_path = pkg_resources.resource_filename(__name__, f"data/quotes/{language}.json")
            text, author, length = select_random_quote(data_path)
        else:
            data_path = pkg_resources.resource_filename(__name__, f"data/words/{language[0:2]}-1000.txt")
            text = select_random_words(data_path, words)
            text = ' '.join(text)

    clear_console()
    Screen.wrapper(intro)

    start_time = time.time()
    text_input = curses.wrapper(game, text, language)
    end_time = time.time()

    wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak = calculate_stats(text, text_input, start_time, end_time)

    save_game_data(wpm, accuracy)

    time.sleep(0.5)

    print_game_statistics(wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak, language)
    plot_statistics(language)

    if language == "chinese":
        typer.echo("\n游戏结束。按 'q' 退出或 'r' 重新开始")
        while True:
            key = typer.getchar()
            if key == "q":
                break
            elif key == "r":
                clear_console()
                start_time = time.time()
                text_input = []
                text_input = curses.wrapper(game, text, language)
                end_time = time.time()
                wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak = calculate_stats(text, text_input, start_time, end_time)
                save_game_data(wpm, accuracy)
                print_game_statistics(wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak, language)
                plot_statistics(language)
                typer.echo("\n游戏结束。按 'q' 退出或 'r' 重新开始")
            else:
                typer.echo("无效按键。按 'q' 退出或 'r' 重新开始")
    else:
        typer.echo("\nThe game has finished. Press 'q' to quit or 'r' to restart")
        while True:
            key = typer.getchar()
            if key == "q":
                break
            elif key == "r":
                clear_console()
                start_time = time.time()
                text_input = []
                text_input = curses.wrapper(game, text, language)
                end_time = time.time()
                wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak = calculate_stats(text, text_input, start_time, end_time)
                save_game_data(wpm, accuracy)
                print_game_statistics(wpm, accuracy, total_letters, correct_letters, incorrect_letters, max_streak, language)
                plot_statistics(language)
                typer.echo("\nThe game has finished. Press 'q' to quit or 'r' to restart")
            else:
                typer.echo("Invalid key. Press 'q' to quit or 'r' to restart")

@app.command()
def help():
    clear_console()
    help_text = pyfiglet.figlet_format("帮助", font="slant")
    
    print("\n")
    print(help_text)
    print("欢迎使用 TyPyn，一个基于终端的打字游戏。")
    print("\n使用方法:")
    print("    typyn [选项] 命令 [参数]")
    print("\n选项:")
    print("    run                         运行游戏")
    print("    version                     查看当前版本")
    print("    show-languages              显示所有可用语言")
    print("    delete-saves                删除所有保存数据")
    print("    --install-completion        为当前shell安装自动补全")
    print("    --show-completion           显示当前shell的自动补全配置")
    print("\n命令:")
    print("    --lang TEXT                 选择游戏语言")
    print("    --words INTEGER             设置游戏字数")
    print("    --timer INTEGER             设置游戏时间")
    print("    --quotes BOOL               使用名言模式")
    print("    --save BOOL                 是否保存统计数据")
    print("\n参数:")
    print("    <值>")
    print("\n")

    time.sleep(1.5)

@app.command()
def version(version : bool = typer.Option(None, "--version", "--v", help="Check current version")):

	clear_console()
	typy_text = pyfiglet.figlet_format(f"TyPyn {VERSION}", font="larry3d")

	typer.echo(f"{typy_text}")

	time.sleep(1.5)

@app.command()
def show_languages(show_languages: bool = typer.Option(None, "--show-languages", "--showl", help="显示所有可用语言")):
    clear_console()
    print("╔════════════════════════════════════╗")
    print("║           可用语言                 ║")
    print("╚════════════════════════════════════╝")

    for language in ALL_LANGUAGES:
        time.sleep(0.7)
        print(f"║  {language['flag']} {language['name'].ljust(16)}" + " "*(20 - len(language['name'])) + "║")

    print(' ' + "═"*36)

@app.command()
def delete_saves():
    try:
        confirmation = input("确定要删除所有历史数据吗？(yes/no): ").lower()
        if confirmation == "yes":
            user_path = pkg_resources.resource_filename(__name__, f"user_data/player_data.json") 
            with open(user_path, 'w') as json_file:
                json_file.truncate(0)
            print("所有历史数据已删除。")
        else:
            print("操作已取消。未删除任何数据。")
    except FileNotFoundError:
        print("历史数据文件不存在。")

if __name__ == "__main__":
	app()