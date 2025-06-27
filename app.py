import random
import os
import time
import sys
import pygame
from pygame import mixer
import toga
from toga import Box, Button, Label, TextInput, ScrollContainer, DetailedList
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import threading


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Инициализация pygame для звуков
pygame.mixer.init()

# Пути к файлам
WORDS_FILE = resource_path("words.txt")
SOUND_CORRECT = resource_path("correct.wav")
SOUND_WRONG = resource_path("wrong.wav")


class WordPairApp:
    def __init__(self):
        # Стили
        self.bg_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.main_color = "#0f3460"
        self.accent_color = "#e94560"
        self.text_color = "#f1f1f1"
        self.correct_color = "#4CAF50"
        self.wrong_color = "#F44336"
        self.second_color = "#34495e"

        # Загрузка слов
        self.words = self.load_words()

        # Переменные
        self.pairs = []
        self.current_pair_index = 0
        self.score = 0
        self.total_questions = 0
        self.test_mode = False
        self.current_question = None
        self.delay = 3
        self.amount = 10

        # Создание приложения
        self.app = toga.App(
            "Memory Master",
            "org.memorymaster",
            startup=self.startup
        )

    def startup(self, app):
        # Основной контейнер
        self.main_box = Box(style=Pack(direction=COLUMN, background_color=self.bg_color))

        # Создаем главное меню
        self.create_main_menu()

        # Возвращаем основной контейнер
        return self.main_box

        # Создаем основное окно
        self.main_window = toga.MainWindow(title="Memory Master", size=(1200, 800))
        self.main_window.content = ScrollContainer(content=self.main_box)
        return self.main_window

    def load_words(self):
        try:
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return [word.strip() for word in content.split(",") if word.strip()]
        except:
            return []

    def save_words(self):
        with open(WORDS_FILE, "w", encoding="utf-8") as f:
            f.write(",".join(self.words))

    def generate_pairs(self, amount):
        if len(self.words) < 2:
            self.show_error("Ошибка", "Недостаточно слов в базе. Добавьте больше слов.")
            return False

        self.pairs = []
        for _ in range(amount):
            word1, word2 = random.sample(self.words, 2)
            self.pairs.append((word1, word2))
        return True

    def clear_main_box(self):
        """Очищаем основной контейнер"""
        while len(self.main_box.children) > 0:
            self.main_box.remove(self.main_box.children[0])

    def create_main_menu(self):
        self.clear_main_box()
        self.test_mode = False

        # Стили
        title_style = Pack(font_size=48, font_weight="bold", color=self.accent_color, padding_bottom=30)
        subtitle_style = Pack(font_size=24, color=self.text_color, padding_bottom=50)
        button_style = Pack(
            font_size=28,
            font_weight="bold",
            color=self.text_color,
            background_color=self.main_color,
            padding=15,
            flex=1,
            width=400
        )
        exit_button_style = button_style.copy()
        exit_button_style.update(background_color=self.wrong_color)

        # Заголовок
        title_label = Label("Memory Master", style=title_style)
        subtitle_label = Label("Тренажер для запоминания пар слов", style=subtitle_style)

        # Кнопки меню
        button_box = Box(style=Pack(direction=COLUMN, padding=10))

        start_button = Button(
            "Начать обучение",
            on_press=lambda widget: self.create_learning_settings(),
            style=button_style
        )

        words_button = Button(
            "Управление словами",
            on_press=lambda widget: self.create_words_management(),
            style=button_style
        )

        exit_button = Button(
            "Выход",
            on_press=lambda widget: self.app.exit(),
            style=exit_button_style
        )

        # Авторские права
        copyright_label = Label("© 2023 Memory Master", style=Pack(font_size=12, color="#aaaaaa", padding_top=50))

        # Добавляем элементы
        self.main_box.add(title_label)
        self.main_box.add(subtitle_label)
        button_box.add(start_button)
        button_box.add(words_button)
        button_box.add(exit_button)
        self.main_box.add(button_box)
        self.main_box.add(copyright_label)

    def show_error(self, title, message):
        """Показать сообщение об ошибке"""
        self.app.main_window.info_dialog(title, message)

    def create_learning_settings(self):
        self.clear_main_box()

        # Стили
        title_style = Pack(font_size=28, font_weight="bold", color=self.text_color, padding_bottom=30)
        label_style = Pack(font_size=18, color=self.text_color, width=200, padding_right=10)
        slider_style = Pack(flex=1, width=400)
        button_style = Pack(font_size=28, color=self.text_color, background_color=self.main_color, padding=10,
                            width=180)
        back_button_style = button_style.copy()
        back_button_style.update(background_color=self.wrong_color)

        # Заголовок
        title_label = Label("Настройки обучения", style=title_style)

        # Контейнер настроек
        settings_box = Box(style=Pack(direction=COLUMN, padding=30, background_color=self.card_color))

        # Количество пар
        amount_box = Box(style=Pack(direction=ROW, padding=15))
        amount_label = Label("Количество пар:", style=label_style)
        self.amount_slider = toga.Slider(
            range=(5, 50),
            value=self.amount,
            style=slider_style
        )
        amount_box.add(amount_label)
        amount_box.add(self.amount_slider)

        # Время показа
        time_box = Box(style=Pack(direction=ROW, padding=15))
        time_label = Label("Время показа (сек):", style=label_style)
        self.time_slider = toga.Slider(
            range=(1, 5),
            value=self.delay,
            style=slider_style
        )
        time_box.add(time_label)
        time_box.add(self.time_slider)

        # Кнопки
        button_box = Box(style=Pack(direction=ROW, padding_top=30))
        start_button = Button(
            "Начать",
            on_press=lambda widget: self.start_learning(),
            style=button_style
        )
        back_button = Button(
            "Назад",
            on_press=lambda widget: self.create_main_menu(),
            style=back_button_style
        )
        button_box.add(start_button)
        button_box.add(back_button)

        # Собираем интерфейс
        settings_box.add(amount_box)
        settings_box.add(time_box)
        settings_box.add(button_box)

        self.main_box.add(title_label)
        self.main_box.add(settings_box)

    def start_learning(self):
        self.amount = int(self.amount_slider.value)
        self.delay = int(self.time_slider.value)

        if not self.generate_pairs(self.amount):
            return

        self.current_pair_index = 0
        self.score = 0
        self.total_questions = 0
        self.test_mode = False

        self.show_next_pair()

    def show_next_pair(self):
        self.clear_main_box()

        if self.current_pair_index >= len(self.pairs):
            self.start_testing()
            return

        word1, word2 = self.pairs[self.current_pair_index]
        self.current_pair_index += 1

        # Показываем пару через дефис
        pair_text = f"{word1} - {word2}"
        self.pair_label = Label(
            pair_text,
            style=Pack(
                font_size=20,
                font_weight="bold",
                color=self.accent_color,
                padding=100,
                text_align=CENTER
            )
        )

        self.main_box.add(self.pair_label)

        # Запускаем анимацию в отдельном потоке
        threading.Thread(target=self.animate_text).start()

        # Переход к следующей паре через заданное время
        threading.Timer(self.delay, self.show_next_pair).start()

    def animate_text(self):
        """Анимация увеличения текста"""
        for size in range(20, 49, 2):
            self.pair_label.style.font_size = size
            time.sleep(0.02)

    def start_testing(self):
        self.test_mode = True
        self.current_pair_index = 0
        self.score = 0
        self.total_questions = len(self.pairs)
        random.shuffle(self.pairs)

        self.ask_question()

    def ask_question(self):
        self.clear_main_box()

        if self.current_pair_index >= len(self.pairs):
            self.show_results()
            return

        word1, word2 = self.pairs[self.current_pair_index]

        # Случайный выбор направления вопроса
        if random.choice([True, False]):
            self.current_question = (word1, word2)
            question = word1
        else:
            self.current_question = (word2, word1)
            question = word2

        # Вопрос
        question_label = Label(
            f"Какое слово было в паре с '{question}'?",
            style=Pack(
                font_size=28,
                font_weight="bold",
                color=self.text_color,
                padding=50,
                text_align=CENTER
            )
        )

        # Поле ввода
        self.answer_input = TextInput(
            style=Pack(
                font_size=28,
                padding=20,
                width=400,
                background_color=self.second_color,
                color=self.text_color
            )
        )

        # Кнопка ответа
        submit_button = Button(
            "Ответить",
            on_press=lambda widget: self.check_answer(),
            style=Pack(
                font_size=28,
                background_color=self.main_color,
                color=self.text_color,
                padding=20,
                width=200
            )
        )

        # Контейнер
        container = Box(style=Pack(direction=COLUMN, padding=20))
        container.add(question_label)
        container.add(self.answer_input)
        container.add(submit_button)

        self.main_box.add(container)

    def check_answer(self):
        answer = self.answer_input.value.strip().lower()
        correct_answer = self.current_question[1].lower()

        if answer == correct_answer:
            self.score += 1
            self.play_sound(SOUND_CORRECT)
            self.show_feedback(True)
        else:
            self.play_sound(SOUND_WRONG)
            self.show_feedback(False, correct_answer)

        # Переход к следующему вопросу через 2 секунды
        threading.Timer(2, self.next_question).start()

    def play_sound(self, sound_file):
        try:
            sound = mixer.Sound(sound_file)
            sound.play()
        except:
            pass

    def show_feedback(self, is_correct, correct_answer=None):
        self.clear_main_box()

        if is_correct:
            text = "Правильно!"
            color = self.correct_color
        else:
            text = f"Неправильно! Правильный ответ: {correct_answer}"
            color = self.wrong_color

        feedback_label = Label(
            text,
            style=Pack(
                font_size=36,
                font_weight="bold",
                color=color,
                padding=100,
                text_align=CENTER
            )
        )

        self.main_box.add(feedback_label)

    def next_question(self):
        self.current_pair_index += 1
        self.ask_question()

    def show_results(self):
        self.clear_main_box()

        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0

        # Результаты
        result_text = f"Результаты тестирования\n\n" \
                      f"Правильных ответов: {self.score}/{self.total_questions}\n" \
                      f"Процент правильных: {percentage:.1f}%"

        result_label = Label(
            result_text,
            style=Pack(
                font_size=28,
                color=self.text_color,
                padding=50,
                text_align=CENTER
            )
        )

        # Кнопки
        button_box = Box(style=Pack(direction=COLUMN, padding=20, width=400))

        restart_button = Button(
            "Начать заново",
            on_press=lambda widget: self.create_learning_settings(),
            style=Pack(
                font_size=28,
                background_color=self.main_color,
                color=self.text_color,
                padding=15
            )
        )

        menu_button = Button(
            "Главное меню",
            on_press=lambda widget: self.create_main_menu(),
            style=Pack(
                font_size=28,
                background_color=self.accent_color,
                color=self.text_color,
                padding=15
            )
        )

        button_box.add(restart_button)
        button_box.add(menu_button)

        self.main_box.add(result_label)
        self.main_box.add(button_box)

    def create_words_management(self):
        self.clear_main_box()

        # Стили
        title_style = Pack(font_size=28, font_weight="bold", color=self.text_color, padding_bottom=20)
        button_style = Pack(font_size=18, color=self.text_color, padding=10, width=120)
        input_style = Pack(font_size=18, padding=10, background_color=self.second_color, color=self.text_color)

        # Заголовок
        title_label = Label("Управление словами", style=title_style)

        # Список слов (используем DetailedList вместо List)
        self.words_list = DetailedList(
            data=[{'word': word} for word in self.words],
            accessors=['word'],
            style=Pack(flex=1, padding=10, background_color=self.second_color, color=self.text_color)
        )

        scroll_container = ScrollContainer(
            content=self.words_list,
            style=Pack(flex=1, height=300, padding_bottom=20)
        )

        # Управление
        control_box = Box(style=Pack(direction=ROW, padding_bottom=20))

        add_button = Button(
            "Добавить",
            on_press=lambda widget: self.add_word(),
            style=button_style.copy(background_color=self.main_color)
        )

        remove_button = Button(
            "Удалить",
            on_press=lambda widget: self.remove_word(),
            style=button_style.copy(background_color=self.wrong_color)
        )

        clear_button = Button(
            "Очистить все",
            on_press=lambda widget: self.clear_words(),
            style=button_style.copy(background_color=self.accent_color)
        )

        control_box.add(add_button)
        control_box.add(remove_button)
        control_box.add(clear_button)

        # Поле ввода
        self.word_input = TextInput(style=input_style)

        # Кнопка назад
        back_button = Button(
            "Назад",
            on_press=lambda widget: self.create_main_menu(),
            style=Pack(
                font_size=28,
                background_color=self.main_color,
                color=self.text_color,
                padding=10,
                width=200
            )
        )

        # Собираем интерфейс
        self.main_box.add(title_label)
        self.main_box.add(scroll_container)
        self.main_box.add(control_box)
        self.main_box.add(self.word_input)
        self.main_box.add(back_button)

        self.word_input.focus()

    def update_words_list(self):
        self.words_list.data = [{'word': word} for word in self.words]

    def add_word(self):
        new_word = self.word_input.value.strip()
        if new_word:
            if new_word not in self.words:
                self.words.append(new_word)
                self.save_words()
                self.update_words_list()
                self.word_input.value = ""
                self.app.main_window.info_dialog("Успех", f"Слово '{new_word}' добавлено!")
            else:
                self.show_error("Внимание", "Это слово уже есть в списке!")
        else:
            self.show_error("Внимание", "Введите слово!")

    def remove_word(self):
        if self.words_list.selection:
            word = self.words_list.selection.word
            self.words.remove(word)
            self.save_words()
            self.update_words_list()
            self.app.main_window.info_dialog("Успех", f"Слово '{word}' удалено!")
        else:
            self.show_error("Внимание", "Выберите слово для удаления!")

    def clear_words(self):
        if self.app.main_window.question_dialog(
                "Подтверждение",
                "Вы уверены, что хотите удалить все слова?"
        ):
            self.words = []
            self.save_words()
            self.update_words_list()
            self.app.main_window.info_dialog("Успех", "Все слова удалены!")

    def run(self):
        return self.app


def main():
    return WordPairApp().app

if __name__ == "__main__":
    app = main()
    app.main_loop()