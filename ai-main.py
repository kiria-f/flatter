import json
import os
import random
import traceback
from dataclasses import dataclass
from typing import Any, NewType, Optional, Union

import readchar
from rich.box import SIMPLE
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

DEBUG = False

# Типы данных
insertion_any_form = NewType(
    'insertion_any_form',
    Union[str, tuple[str, int], tuple[str, ...], list[str], tuple[tuple[str, int], ...], list[tuple[str, int]]],
)

insertion = NewType('insertion', list[tuple[str, int]])

# Раскладки клавиатуры
en_keyboard = '`qwertyuiop[]asdfghjkl;\'zxcvbnm,./~QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?'
ru_keyboard = 'ёйцукенгшщзхъфывапролджэячсмитьбю.ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,'
en2ru = {e: r for e, r in zip(en_keyboard, ru_keyboard)}
ru2en = {r: e for e, r in zip(en_keyboard, ru_keyboard)}


# Стили
class Styles:
    PHRASE = Style(color='bright_blue', bold=True)
    DELIM = Style(color='default')
    TRANSLATION = Style(color='green')
    ERROR = Style(color='red')
    WARNING = Style(color='yellow')
    HIGHLIGHT = Style(bgcolor='grey23')
    MENU_ITEM = Style(color='green', bold=True)
    MENU_TITLE = Style(color='bright_blue', bold=True)
    SELECTED = Style(bgcolor='blue', bold=True)


@dataclass
class Record:
    translation: str
    rate: float = 1.0


class RecordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Record):
            return obj.__dict__
        return super().default(obj)


class DB:
    data: dict[str, Record] = {}
    init_size: int = 0

    @staticmethod
    def load(config: Optional[dict[str, str]] = None) -> bool:
        try:
            if config is None:
                with open('config.json', 'r', encoding='utf-8') as config_file:
                    config = json.load(config_file)
            with open(config['db-path'], 'r', encoding='utf-8') as db_file:
                db_raw = json.load(db_file)
            DB.data = {k: Record(v['translation'], v['rate']) for k, v in db_raw.items()}
            DB.init_size = len(DB.data)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    @staticmethod
    def save(config: Optional[dict[str, str]] = None) -> None:
        if config is None:
            with open('config.json', 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)

        if len(DB.data) >= DB.init_size:
            with open(config['db-path'] + '.bak', 'w', encoding='utf-8') as db_file_backup:
                json.dump(DB.data, db_file_backup, cls=RecordEncoder, ensure_ascii=False, indent=4)

        with open(config['db-path'], 'w', encoding='utf-8') as db_file:
            json.dump(DB.data, db_file, cls=RecordEncoder, ensure_ascii=False, indent=4)


class Key:
    class Special:
        PRINTABLE = 0
        ENTER = 1
        BACKSPACE = 2
        TAB = 3
        ESCAPE = 4
        SHIFT = 5
        CTRL = 6
        HOME = 7
        END = 8
        DELETE = 9
        ARROW_UP = 10
        ARROW_DOWN = 11
        ARROW_LEFT = 12
        ARROW_RIGHT = 13

    def __init__(self, value: Union[str, int]):
        if isinstance(value, str):
            self.printable = value
            self.special = Key.Special.PRINTABLE
        else:
            self.special = value
            self.printable = ''

    def __eq__(self, other):
        if isinstance(other, str):
            return self.printable == other
        if isinstance(other, int):
            return self.special == other
        return super().__eq__(other)

    def __str__(self):
        return self.printable


class State:
    class Enum:
        MENU = 'menu'
        SCROLL = 'scroll'
        ADD = 'add'
        EXPLORE = 'explore'
        QUIT = 'quit'
        EDIT = 'edit'

    state = Enum.MENU
    parameter: Any = None
    input = ''
    cursor_index = -1
    first_time = True


class AppUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.layout.split_column(
            Layout(name='header', size=3), Layout(name='main', ratio=1), Layout(name='footer', size=3)
        )
        self.current_display = None
        self.setup_menu()

    def clear(self):
        self.console.clear()

    def setup_menu(self):
        menu_table = Table.grid(padding=(1, 2))
        menu_table.add_column(justify='center')
        menu_table.add_row('[green][A][/] Add Phrase')
        menu_table.add_row('[green][E][/] Explore')
        menu_table.add_row('[green]Enter[/] Run Training')
        menu_table.add_row('[green][R][/] Refresh')
        menu_table.add_row('[red][Q][/] Quit')

        self.layout['main'].update(
            Panel(menu_table, title='[bright_blue]Trans Dictionary[/]', border_style='bright_blue')
        )
        self.layout['footer'].update(Panel('Press [green]ESC[/] to return to menu from anywhere', border_style='dim'))

    def show_message(self, message: str, style: Style = Styles.WARNING):
        self.layout['footer'].update(Panel(Text(message, style=style), border_style='dim'))

    def show_add_screen(self, prompt: str, suggestions: list[tuple[str, str]] = []):
        main_panel = Table.grid(padding=(0, 1))
        main_panel.add_column()

        # Поле ввода
        input_line = Text('> ') + Text(prompt, style='bold')
        main_panel.add_row(input_line)

        # Подсказка формата
        format_hint = Text()
        if ' - ' in prompt:
            phrase_part, trans_part = prompt.split(' - ', 1)
            format_hint.append('Phrase: ', style=Styles.PHRASE)
            format_hint.append(phrase_part[:10], style=Styles.PHRASE)
            if len(phrase_part) > 10:
                format_hint.append('...', style=Styles.PHRASE)
            format_hint.append(' - ', style=Styles.DELIM)
            format_hint.append('Translation: ', style=Styles.TRANSLATION)
            format_hint.append(trans_part[:10], style=Styles.TRANSLATION)
            if len(trans_part) > 10:
                format_hint.append('...', style=Styles.TRANSLATION)
        else:
            format_hint.append('Phrase...', style=Styles.PHRASE)

        main_panel.add_row(format_hint)

        # Подсказки
        if suggestions:
            suggestions_table = Table.grid(padding=(0, 2))
            suggestions_table.add_column()
            for phrase, trans in suggestions[:5]:
                suggestions_table.add_row(f'• {phrase} - {trans}')
            main_panel.add_row('\nSuggestions:')
            main_panel.add_row(suggestions_table)

        self.layout['main'].update(Panel(main_panel, title='[green]Add New Phrase[/]', border_style='green'))
        self.current_display = 'add'

    def show_explore_screen(self, prompt: str, items: list[tuple[str, Record]], selected: int = -1):
        main_table = Table.grid(padding=(0, 1))
        main_table.add_column()

        # Поле поиска
        search_line = Text('Search: ') + Text(prompt, style='bold')
        main_table.add_row(search_line)
        main_table.add_row(Text('Press [green]TAB[/] to switch search direction'))

        # Список фраз
        if items:
            items_table = Table(box=SIMPLE, padding=(0, 1))
            items_table.add_column('Phrase')
            items_table.add_column('Translation')
            items_table.add_column('Rate', justify='right')

            for i, (phrase, record) in enumerate(items):
                if i == selected:
                    items_table.add_row(
                        Text(phrase, style='bold'),
                        Text(record.translation, style='bold'),
                        Text(f'{record.rate:.2f}', style='bold'),
                        style=Styles.HIGHLIGHT,
                    )
                else:
                    items_table.add_row(phrase, record.translation, f'{record.rate:.2f}')

            main_table.add_row(items_table)
            main_table.add_row(
                Text('[green][D][/] Delete  [green][E][/] Edit  [green][R][/] Reset selection', style='dim')
            )
        else:
            main_table.add_row(Text('No items found', style=Styles.WARNING))

        self.layout['main'].update(Panel(main_table, title='[green]Explore Dictionary[/]', border_style='green'))
        self.current_display = 'explore'

    def show_edit_screen(self, original: tuple[str, Record], edited: str, cursor_pos: int):
        main_panel = Table.grid(padding=(0, 1))
        main_panel.add_column()

        # Поле редактирования
        edited_text = Text()
        parts = edited.split(' - ', 1)

        edited_text.append(parts[0], style=Styles.PHRASE)
        if len(parts) > 1:
            edited_text.append(' - ', style=Styles.DELIM)
            edited_text.append(parts[1], style=Styles.TRANSLATION)

        main_panel.add_row(Text('Editing: '))
        main_panel.add_row(edited_text)
        main_panel.add_row(Text('\nOriginal: '))
        main_panel.add_row(Text(f'{original[0]} - {original[1].translation}', style='dim'))

        self.layout['main'].update(Panel(main_panel, title='[green]Edit Phrase[/]', border_style='green'))
        self.current_display = 'edit'

    def show_training_screen(self, phrase: str, translation: Optional[str] = None, reveal: bool = False):
        main_panel = Table.grid(padding=(0, 1))
        main_panel.add_column(justify='center')

        if phrase:
            main_panel.add_row(Text(phrase, style=Styles.PHRASE, justify='center'))

            if reveal and translation:
                main_panel.add_row(Text('↓', style='dim', justify='center'))
                main_panel.add_row(Text(translation, style=Styles.TRANSLATION, justify='center'))
            else:
                main_panel.add_row(Text('Press [green]ENTER[/] to reveal translation', style='dim'))

            main_panel.add_row(Text("\n[green]ENTER[/] Correct  [red]'[/] Incorrect", style='dim'))
        else:
            main_panel.add_row(Text('No phrases in database', style=Styles.WARNING))

        self.layout['main'].update(Panel(main_panel, title='[green]Training Mode[/]', border_style='green'))
        self.current_display = 'training'


class TransDictionary:
    def __init__(self):
        self.ui = AppUI()
        self.state = State.Enum.MENU
        self.state_parameter = None
        self.running = True
        self.console = Console()

        # Загрузка конфигурации
        try:
            with open('config.json', 'r', encoding='utf-8') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            self.console.print('[yellow]Config file not found. Creating new one...[/]')
            self.config = {}
            self.setup_config()

        # Загрузка базы данных
        if not DB.load(self.config):
            self.console.print('[red]Database not found.[/]')
            if input('Create new database? [y/N]: ').lower() == 'y':
                self.config['db-path'] = input('Enter database file path: ')
                with open(self.config['db-path'], 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                DB.load(self.config)
            else:
                self.running = False

        # Сохранение конфига
        with open('config.json', 'w', encoding='utf-8') as config_file:
            json.dump(self.config, config_file, indent=4)

    def setup_config(self):
        self.console.print('[bold yellow]Initial setup[/]')
        self.config['db-path'] = input('Enter path for database file: ')

        # Создаем пустую базу, если нужно
        if not os.path.exists(self.config['db-path']):
            with open(self.config['db-path'], 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def get_key(self) -> Key:
        """Упрощенная кросс-платформенная версия с readchar"""
        key = readchar.readkey()

        special_keys = {
            readchar.key.UP: Key.Special.ARROW_UP,
            readchar.key.DOWN: Key.Special.ARROW_DOWN,
            readchar.key.LEFT: Key.Special.ARROW_LEFT,
            readchar.key.RIGHT: Key.Special.ARROW_RIGHT,
            readchar.key.ENTER: Key.Special.ENTER,
            readchar.key.BACKSPACE: Key.Special.BACKSPACE,
            readchar.key.TAB: Key.Special.TAB,
            readchar.key.ESC: Key.Special.ESCAPE,
            readchar.key.HOME: Key.Special.HOME,
            readchar.key.END: Key.Special.END,
            readchar.key.DELETE: Key.Special.DELETE,
        }

        if key in special_keys:
            return Key(special_keys[key])
        return Key(key)

    def handle_menu(self, key: Key):
        if key == 'a':
            self.state = State.Enum.ADD
            self.state_parameter = ''
        elif key == 'e':
            self.state = State.Enum.EXPLORE
            self.state_parameter = {'prompt': '', 'filtered': [], 'selection': -1}
        elif key == Key.Special.ENTER:
            self.state = State.Enum.SCROLL
            self.state_parameter = None
        elif key == 'r':
            self.ui.clear()
        elif key == Key.Special.ESCAPE:
            self.ui.show_message(f'Database contains {len(DB.data)} phrases')
        elif key == 'q':
            self.running = False
        else:
            self.ui.show_message(f'Unknown command: {key}', Styles.ERROR)

    def handle_add(self, key: Key):
        if key == Key.Special.ESCAPE:
            self.state = State.Enum.MENU
            self.state_parameter = None
        elif key == Key.Special.ENTER:
            if ' - ' in self.state_parameter:
                phrase, translation = self.state_parameter.split(' - ', 1)
                DB.data[phrase] = Record(translation)
                DB.save()
                self.ui.show_message(f"Phrase '[bright_blue]{phrase}[/]' added successfully!")
                self.state = State.Enum.MENU
                self.state_parameter = None
            else:
                self.ui.show_message('Format: [bright_blue]phrase[/] - [green]translation[/]', Styles.ERROR)
        elif key == Key.Special.BACKSPACE:
            self.state_parameter = self.state_parameter[:-1]
        else:
            self.state_parameter += str(key)

    def handle_explore(self, key: Key):
        if key == Key.Special.ESCAPE:
            self.state = State.Enum.MENU
            self.state_parameter = None
        elif (
            key == Key.Special.ARROW_UP
            and self.state_parameter['selection'] < len(self.state_parameter['filtered']) - 1
        ):
            self.state_parameter['selection'] += 1
        elif key == Key.Special.ARROW_DOWN and self.state_parameter['selection'] > -1:
            self.state_parameter['selection'] -= 1
        elif key == Key.Special.TAB:
            # Переключение направления поиска (можно реализовать)
            pass
        elif key == Key.Special.BACKSPACE:
            self.state_parameter['prompt'] = self.state_parameter['prompt'][:-1]
            self.update_filtered()
        elif self.state_parameter['selection'] == -1:
            self.state_parameter['prompt'] += str(key)
            self.update_filtered()
        elif key == 'd':
            # Удаление выбранной фразы
            selected = self.state_parameter['filtered'][self.state_parameter['selection']]
            del DB.data[selected[0]]
            DB.save()
            self.update_filtered()
        elif key == 'e':
            # Редактирование
            self.state = State.Enum.EDIT
            selected = self.state_parameter['filtered'][self.state_parameter['selection']]
            self.state_parameter = {
                'original': selected,
                'edited': f'{selected[0]} - {selected[1].translation}',
                'cursor_pos': len(f'{selected[0]} - {selected[1].translation}'),
            }

    def update_filtered(self):
        prompt = self.state_parameter['prompt'].lower()
        if prompt:
            self.state_parameter['filtered'] = [
                (k, v) for k, v in DB.data.items() if prompt in k.lower() or prompt in v.translation.lower()
            ][:10]
        else:
            self.state_parameter['filtered'] = []
        self.state_parameter['selection'] = -1 if not self.state_parameter['filtered'] else 0

    def handle_edit(self, key: Key):
        if key == Key.Special.ESCAPE:
            self.state = State.Enum.EXPLORE
        elif key == Key.Special.ENTER:
            # Сохранение изменений
            original = self.state_parameter['original']
            new_phrase, new_trans = self.state_parameter['edited'].split(' - ', 1)

            # Удаляем старую запись, если изменилась фраза
            if new_phrase != original[0]:
                del DB.data[original[0]]

            # Добавляем/обновляем запись
            DB.data[new_phrase] = Record(new_trans, original[1].rate)
            DB.save()

            self.state = State.Enum.EXPLORE
            self.state_parameter = {'prompt': '', 'filtered': [], 'selection': -1}
        elif key == Key.Special.BACKSPACE:
            if self.state_parameter['cursor_pos'] > 0:
                edited = self.state_parameter['edited']
                self.state_parameter['edited'] = (
                    edited[: self.state_parameter['cursor_pos'] - 1] + edited[self.state_parameter['cursor_pos'] :]
                )
                self.state_parameter['cursor_pos'] -= 1
        elif key == Key.Special.ARROW_LEFT:
            self.state_parameter['cursor_pos'] = max(0, self.state_parameter['cursor_pos'] - 1)
        elif key == Key.Special.ARROW_RIGHT:
            self.state_parameter['cursor_pos'] = min(
                len(self.state_parameter['edited']), self.state_parameter['cursor_pos'] + 1
            )
        else:
            edited = self.state_parameter['edited']
            pos = self.state_parameter['cursor_pos']
            self.state_parameter['edited'] = edited[:pos] + str(key) + edited[pos:]
            self.state_parameter['cursor_pos'] += 1

    def handle_training(self, key: Key):
        if key == Key.Special.ESCAPE:
            self.state = State.Enum.MENU
            self.state_parameter = None
        elif key == Key.Special.ENTER:
            if self.state_parameter is None or not self.state_parameter.get('reveal', False):
                # Показываем перевод
                if self.state_parameter is None:
                    self.state_parameter = self.get_random_phrase()
                self.state_parameter['reveal'] = True
            else:
                # Правильный ответ - уменьшаем рейтинг
                phrase = self.state_parameter['phrase']
                DB.data[phrase].rate *= 0.75
                DB.save()
                self.state_parameter = self.get_random_phrase()
        elif key == "'":
            # Неправильный ответ - увеличиваем рейтинг
            if self.state_parameter and self.state_parameter.get('reveal', False):
                phrase = self.state_parameter['phrase']
                DB.data[phrase].rate *= 1.25
                DB.save()
                self.state_parameter = self.get_random_phrase()

    def get_random_phrase(self) -> dict:
        """Выбирает случайную фразу с учетом рейтинга"""
        if not DB.data:
            return None

        total = sum(r.rate for r in DB.data.values())
        r = random.uniform(0, total)
        current = 0
        for phrase, record in DB.data.items():
            current += record.rate
            if r <= current:
                return {'phrase': phrase, 'translation': record.translation, 'reveal': False}
        return None

    def update_ui(self):
        if self.state == State.Enum.MENU:
            self.ui.setup_menu()
            if self.state_parameter:
                self.ui.show_message(self.state_parameter)
        elif self.state == State.Enum.ADD:
            suggestions = []
            if self.state_parameter and ' - ' in self.state_parameter:
                phrase_part = self.state_parameter.split(' - ')[0].lower()
                suggestions = [(k, v.translation) for k, v in DB.data.items() if phrase_part in k.lower()][:5]
            self.ui.show_add_screen(self.state_parameter, suggestions)
        elif self.state == State.Enum.EXPLORE:
            self.ui.show_explore_screen(
                self.state_parameter['prompt'], self.state_parameter['filtered'], self.state_parameter['selection']
            )
        elif self.state == State.Enum.EDIT:
            self.ui.show_edit_screen(
                self.state_parameter['original'], self.state_parameter['edited'], self.state_parameter['cursor_pos']
            )
        elif self.state == State.Enum.SCROLL:
            if self.state_parameter is None:
                self.state_parameter = self.get_random_phrase()
            self.ui.show_training_screen(
                self.state_parameter['phrase'] if self.state_parameter else '',
                self.state_parameter['translation'] if self.state_parameter else None,
                self.state_parameter['reveal'] if self.state_parameter else False,
            )

    def run(self):
        with Live(self.ui.layout, refresh_per_second=10, screen=True) as live:
            while self.running:
                self.update_ui()
                key = self.get_key()

                if self.state == State.Enum.MENU:
                    self.handle_menu(key)
                elif self.state == State.Enum.ADD:
                    self.handle_add(key)
                elif self.state == State.Enum.EXPLORE:
                    self.handle_explore(key)
                elif self.state == State.Enum.EDIT:
                    self.handle_edit(key)
                elif self.state == State.Enum.SCROLL:
                    self.handle_training(key)


if __name__ == '__main__':
    try:
        app = TransDictionary()
        app.run()
    except Exception as e:
        console = Console()
        console.print(f'[red]Error:[/] {e}')
        traceback.print_exc()
        console.print('\n[yellow]Press any key to exit...[/]')
        input()
