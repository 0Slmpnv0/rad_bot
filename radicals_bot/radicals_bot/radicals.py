import json
from collections import Counter
from beautiful_plot import Graph
from icecream import ic
from os import remove
import random
from telebot import types


class Point:
    i = 0

    def __init__(self, aspect, question, rad_type):
        Point.i += 1
        self.question = question
        self.rad_type = rad_type
        self.aspect = aspect
        self.number = Point.i

    def __str__(self):
        return f'{self.question}'


class Profile:
    def __init__(self, name):
        self.points: dict[int: int] = {}
        for i in range(1, len(points)):
            self.points[i] = -1
        self.name = name

    def __str__(self):
        result: str = ''
        buffer = []
        result += 'Общий психологический профиль:\n'
        for asp, count in self.convert_points_to_radical_stat('total'):
            buffer.append(f'{asp}:{count}')
        result += '\n'.join(buffer)
        buffer = []
        result += '\nВ поведении:\n'
        for asp, count in self.convert_points_to_radical_stat('behaviour'):
            buffer.append(f'{asp}:{count}')
        result += '\n'.join(buffer)
        buffer = []
        result += '\nВо внешности:\n'
        for asp, count in self.convert_points_to_radical_stat('appearance'):
            buffer.append(f'{asp}:{count}')
        result += '\n'.join(buffer)
        buffer = []
        result += '\nВ оформлении окружающего пространства:\n'
        for asp, count in self.convert_points_to_radical_stat('behaviour'):
            buffer.append(f'{asp}:{count}')
        result += '\n'.join(buffer)
        buffer = []
        return result

    def add_points(self, points: dict[int: str] = {}):
        if points:
            for point_num, point_count in points.items():
                self.points[point_num] = point_count
        else:
            for i in range(len(points)):
                self.points[i + 1] = -1

    def convert_points_to_radical_stat(self, asp_type) -> list[tuple[str: int]]:
        result: dict[str: int] = {
            "ИС": 0,
            "ЭП": 0,
            "ПАР": 0,
            "ЭМ": 0,
            "ШИЗ": 0,
            "ГИП": 0,
            "ТРЕВ": 0
        }
        match asp_type:
            case 'total':
                for point_num, point_count in self.points.items():
                    point_count = int(point_count)
                    if point_count < 0:
                        continue
                    key = points[point_num - 1].rad_type
                    result[key] += point_count
            case 'behaviour':
                for point_num, point_count in self.points.items():
                    point_count = int(point_count)
                    if points[point_num - 1].aspect != 'behaviour':
                        continue
                    if point_count < 0:
                        continue
                    key = points[point_num - 1].rad_type
                    result[key] += point_count
            case 'surround_spec':
                for point_num, point_count in self.points.items():
                    point_count = int(point_count)
                    if points[point_num - 1].aspect != 'surround_spec':
                        continue
                    if point_count < 0:
                        continue
                    key = points[point_num - 1].rad_type
                    result[key] += point_count
            case 'appearance':
                for point_num, point_count in self.points.items():
                    point_count = int(point_count)
                    if points[point_num - 1].aspect != 'appearance':
                        continue
                    if point_count < 0:
                        continue
                    key = points[point_num - 1].rad_type
                    result[key] += point_count
        rs = Counter(result)
        return rs.most_common()

    def gen_graph(self, call: types.CallbackQuery):
        x_total_ticks = []
        y_total_ticks = []
        for asp_type in ['behaviour', 'surround_spec', 'appearance', 'total']:
            for rad, count in self.convert_points_to_radical_stat(asp_type):
                y_total_ticks.append(count)
                x_total_ticks.append(rad)
                match asp_type:
                    case 'behaviour':
                        name = f'beh_plot_for_{call.from_user.id}_{call.data}'
                        ylabel = 'Баллы проявления радикалов в поведении человека'
                        label_size = 40
                    case 'surround_spec':
                        name = f'surr_plot_for_{call.from_user.id}_{call.data}'
                        ylabel = 'Баллы проявления радикалов в оформлении окружающего пространства'
                        label_size = 25
                    case 'appearance':
                        name = f'app_plot_for_{call.from_user.id}_{call.data}'
                        ylabel = 'Баллы проявления радикалов во внешности человека'
                        label_size = 40
                    case 'total':
                        name = f'total_plot_for_{call.from_user.id}_{call.data}'
                        ylabel = 'Общие баллы проявления радикалов в личности человека'
                        label_size = 40
            Graph(name, xtick_labels=x_total_ticks, main_axis=y_total_ticks, ylabel=ylabel, label_size=40).save('images')
            x_total_ticks = []
            y_total_ticks = []


    def rm_graph(self, call):
        for path in [
            f'images/total_plot_for_{call.from_user.id}_{call.data}.png',
            f'images/beh_plot_for_{call.from_user.id}_{call.data}.png',
            f'images/app_plot_for_{call.from_user.id}_{call.data}.png',
            f'images/surr_plot_for_{call.from_user.id}_{call.data}.png'
        ]:
            remove(path)


def load_data():
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_data(user_data: dict):
    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump(user_data, file, indent=2, ensure_ascii=False)


isteroid = {
    "appearance": ["Уделяет много внимания своей внешности", "Выделяется на фоне остальных людей",
                   "В основном предпочитает очень яркую, пеструю одежду, но не оригинальную",
                   "Трепетно относится к моде",
                   "Часто использует в качестве украшений бисер, блестки, пайетки"],

    "surround_spec": ["Характерен эгоцентризм(по комнате стоят свои фото/кубки/дипломы)",
                      "Есть подобие коллекций, но скорее для того, чтобы получить статус \"Коллекционера\", "
                      "а не действительно собрать коллекцию.",
                      "В комнате довольно много безделушек: ловцы снов, кольца в коробочках и т.д.",
                      "Большой гардероб"],

    "behaviour": ["Создает \"Иллюзию благополучия и успеха\"", "Часто тянет на себя одеяло",
                  "Пытается понравится людям",
                  "Подражает успешной модели поведения", "Поверхностьный/ая",
                  "Чувство особенной собственной значимости",
                  "Иногда характерны наигранные эмоции", "Пытается причислить себя к какой-то группе",
                  "Не имеет своего мнения",
                  "Одинаково хорошо себя ощущают себя в разных образах", "Не любят ситуации, когда случайно кто-то",
                  "Расстраиваются, когда их внешность не подходит под ситуацию",
                  "Много обещают. Чаще говорят, чем делают", "Создают видимость дела",
                  "Искренне убежден/на, что способен на что угодно",
                  "Плохо хранят секреты", "Терпеть не может рутину"],

    "goal": ''}

epil = {
    "appearance": ["Большая мышечная масса. Массивный торс, короткая шея. Не пропорционален/на",
                   "Одевается функционально",
                   "Одежда соответствует ситуации", "Короткая стрижка", "Всегда идеально чистая одежда",
                   "НЕТ БОРОД И ДЛИННЫХ НОГТЕЙ"],
    "surround_spec": ["Всё идеально чисто", "Всё на своих местах", "Нет бесполезных вещей",
                      "Всё использует по-назначению",
                      "На рабочем столе порядок", "Создание картотек/таблиц и т.д."],
    "behaviour": ["Человеконенавистничество", "Всегда исправляет мелкие недочеты", "Любит уборку",
                  "Не позволяет трогать свои вещи",
                  "Делит людей на “сильных” и “слабых”", "Берет вещи без спроса (пока не “обожжется”)", "Абьюз",
                  "Не брезгует жертвами"],
    "goal": "\"Выдрессировать\" людей. \"Построить в шеренгу\". Стремится объединить и возглавить коллектив, но не может продвинуться дальше наведения порядка"

}

paran = {
    "appearance": ["Классицизм", "Унификация формы", "Предпочитает различную символику, знаки принадлежности"],
    "surround_spec": ["На стенах часто развешивает символику своей \"Партии\"", "Все окружение связано с работой"],
    "behaviour": ["Единица- ничто. Считает людей миллионами, тысячами", "Разговаривает о будущем, о потомках.",
                  "Часто берет на себя настоящую ответственность",
                  "Может и работает везде, где можно и нельзя (за столом, в кровати, в ванной и тд)",
                  "Искеренняя вера в свою исключительную правоту", "Размашистая, активная жестикуляция"],
    "goal": "Объединить людей для исполнения великой цели"}

emote = {
    "appearance": ["Гармоничная, стильная внешность", "Умеет завуалировать недостатки внешности",
                   "Не любят острые углы",
                   "Свободная одежда, оверсайз, толстовки и тд", "Печальные, задумчивые, добрые глаза"],
    "surround_spec": ["Различные предметы искусства", "Музыкальные инструменты", "Книги"],
    "behaviour": ["Чувствует настроение коллектива", "Плавные, женственные движения",
                  "Удобные, свободные, не стесняющие окружающих позы",
                  "Сопереживающий, понимающий", "Выше всего ставит проблемы отдельных людей",
                  "Не может причинить физического/психологического вреда",
                  "Неконфликтный/ая", "Бескорыстный/ая", "Жертвенный/ая", "Человеколюбивый/ая", "Ранимый/ая"],
    "goal": ""}

shiz = {
    "appearance": ["Астеническое телосложение", "Не органично выглядит (пиджак и дырявые треники). Как клоун",
                   "Неопрятный. Игнорирует недостатки внешности, или очень неумело их закрывает", "Длинные волосы",
                   "Растительность на лице", "Любит капюшоны, темные очки", "Таскает с собой рюкзак со всяким хламом"],
    "surround_spec": ["Захламляет всё, и свое, и чужое: “скляночки, баночки”"],
    "behaviour": ["Угловатые, резкие, плохо координированные движения", "Не ортодоксальное мышление",
                  "Богатая фантазия, творческий/ая",
                  "Плохая концентрация", "Отрицает аксиомы, БАЗУ", "Ничему не верит", "Ленивый/ая",
                  "Очень мало энергии",
                  "Он(а) лучше замаскирует недостатки, чем исправит их",
                  "Вечно спорит с обществомна это тратит ту немногую энергию, которая у него есть)",
                  "Хорошее чувство юмора, веселый",
                  "После долгих рассуждений приходят к выводу, с самого начала очевидному для остальных", "Наивный",
                  "Пути достижения целей не логичные"],
    "goal": ""}

hypertim = {
    "appearance": ["Одежда для отдыха (суббота начинается в понедельник)", "Торопливая небрежность",
                   "Большая гостеприимность"],
    "surround_spec": ["Хаотичное жилище"],
    "behaviour": ["Жизнерадостный оптимист", "Нет цели, есть только путь", "Всё делает на бегу", "Всё хочет опробовать",
                  "Делает всё “не стесняясь”", "Неаккуратный/ая, суетливые", "Не понимает значения труда",
                  "Не любит виртуальную реальность",
                  "Любит активный отдых, путешествия. Имеет всё, что для этого нужно"],
    "goal": ""
}

anxiet = {
    "appearance": [],
    "surround_spec": [],
    "behaviour": [],
    "goal": ""
}

points: list[Point] = []
for rad, rad_type in zip([isteroid, epil, paran, emote, shiz, hypertim], ['ИС', 'ЭП', 'ПАР', 'ЭМ', 'ШИЗ', 'ГИП']):
    for asp in ["appearance", "surround_spec", "behaviour", "goal"]:
        if type(rad[asp]) == list:
            for point in rad[asp]:
                points.append(Point(aspect=asp, question=point, rad_type=rad_type))
        elif not rad[asp]:
            continue
        else:
            points.append(Point(aspect=asp, question=rad[asp], rad_type=rad_type))

