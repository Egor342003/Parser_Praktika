import random
from termcolor import colored, cprint
import datetime
import re

user_name = input('Пожалуйста, введите своё имя.\nСпасибо, ')
SUCCESS = "SUCCESS"
FAILED = "FAILED"


def regex_or(lst):
    lst = ["(" + el + ")" for el in lst]
    res = f"({'|'.join(lst)})"
    return res


def regex_or_var(lst, var_name):
    lst = ["(" + el + ")" for el in lst]
    res = f"(?P<{var_name}>{'|'.join(lst)})"
    return res


def var(txt, var_name):
    res = f"(?P<{var_name}>{txt})"
    return res


def find_dict_match(exact_value, map_dict):
    for key, regex_value in map_dict.items():
        m = re.search(regex_value, exact_value)
        if m:
            return key
    return None


def parse_message(message):
    res, matches = {}, []
    for pattern in patterns:
        message_low = message.lower()
        m = re.search(pattern, message_low)
        if m:
            matches.append(m)
            res.update(m.groupdict())
    return res, matches


def highlight_message(message, matches, **print_kwargs):
    if not matches:
        cprint(message, 'blue', **print_kwargs)
        return None
    matches.sort(key=lambda x: x.start())
    colored_msg = ''
    first, last = matches[0], matches[-1]
    colored_msg += colored(message[0:first.start()], 'blue')
    for i, match in enumerate(matches):
        colored_msg += colored(message[match.start():match.end()], 'green')
        if match is not last:
            colored_msg += colored(message[match.end():matches[i+1].start()], 'blue')
    colored_msg += colored(message[last.end():len(message)], 'blue')
    print(colored_msg, **print_kwargs)


def get_task(message, matches):
    if not matches:
        return None
    matches.sort(key=lambda x: x.start())
    task_list = []
    first, last = matches[0], matches[-1]
    task_list.append(message[0:first.start()].strip()) if message[0:first.start()].strip() else None
    for i, match in enumerate(matches):
        if match is not last:
            task_list.append(message[match.end():matches[i + 1].start()].strip()) if message[match.end():matches[i + 1].start()].strip() else None

    task_list.append(message[last.end():len(message)].strip()) if message[last.end():len(message)].strip() else None
    if not task_list:
        return None
    else:
        return ' '.join(task_list)


relative_days = ["сегодня", "завтра", "послезавтра"]
part_of_day = ["(с )?утра?(ом)?", "дн[её]м", "вечером", "ночью"]
every = ["кажд[ыоу][йею]", "по"]
days_of_weeks = {
    0: "понедельник(ам)?", 
    1: "вторник(ам)?",
    2: "среду?(ам)?",
    3: "четверг(ам)?",
    4: "пятницу?(ам)?",
    5: "субботу?(ам)?",
    6: "воскресенье?(ям)?"
}
months = {
    0: "числа",
    1: "январ[ья]",
    2: "феврал[ья]",
    3: "март[а]?",
    4: "апрел[ья]",
    5: "ма[йя]",
    6: "июн[ья]",
    7: "июл[ья]",
    8: "август[а]?",
    9: "сентябр[ья]",
    10: "октябр[ья]",
    11: "ноябр[ья]",
    12: "декабр[ья]",
}
time_measure = dict(
    years=regex_or(["год[ау]?", "лет"]),
    months="месяц[ае]?",
    weeks="недел[юие]",
    days="де?н[яье][й]?",
    hours="час[а]?(ов)?",
    minutes="минут[уы]?",
    day='числ[оа]',
    days_of_weeks=regex_or(list(days_of_weeks.values())),
    weekend='выходны[емх]'
)
all_dct = list(time_measure.values())

# The main patterns
year_pattern = f'{var("[2-3][0-1][0-9][0-9]", "year")} (года?)?'
day_week_pattern = f'во? {regex_or_var(list(days_of_weeks.values()), "days_of_week")}'
day_pattern = f'{var("[0-9]{1,2}", "day")} {regex_or_var(list(months.values()), "month")}'
time_pattern = f'в? (?P<hours>\d{1,2}):(?P<minutes>\d{2})'

every_pattern = f'{regex_or_var(every, "every")} (?P<amount>\d*)\s?{regex_or_var(all_dct, "time_range")}'
after_pattern = f'{var("через", "after")} (?P<amount>\d*)\s?{regex_or_var(all_dct, "time_range")}'

relative_pattern = f"{regex_or_var(relative_days, 'relative')}"
part_of_day_pattern = f"{regex_or_var(part_of_day, 'part_of_day')}"

on_pattern = 'на\s(?P<week_weekend>(неделе)|(выходны[хм]))'
on_next_pattern = f'{regex_or(["на", "в"])} следующ[ие][йм] {regex_or_var(list(time_measure.values()), "time_range")}'

patterns = [time_pattern, every_pattern, day_week_pattern, day_pattern, year_pattern, relative_pattern,
            part_of_day_pattern, on_pattern, on_next_pattern, after_pattern]


with open('examples.txt', encoding='utf-8') as file:
    examples = file.read().splitlines()


def relative_def(res, json_output):
    relative = res['relative']
    if relative == 'завтра':
        day_add = 1
    elif relative == 'послезавтра':
        day_add = 2
    else:
        day_add = 0
    datetime_after = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month'])) + datetime.timedelta(days=day_add)
    day = datetime_after.day
    month = datetime_after.month

    json_output['DATE']['day'] = day
    json_output['DATE']['month'] = month


def week_weekend_def(res, json_output):
    weekday_rand = None
    day_every = None
    weekday = datetime.datetime.now().weekday()

    if res['week_weekend'] == 'неделе':
        if weekday == 4:
            weekday_rand = random.randint(0, 4)
        else:
            if weekday == 6:
                number_one = 0
            else:
                number_one = weekday + 1
            weekday_rand = random.randint(number_one, 4)
    elif res['week_weekend'] in 'выходнымвыходных':
        weekday_rand = random.randint(5, 6)

    if weekday_rand < int(weekday):
        day_every = weekday_rand - weekday + 7
    elif weekday_rand == weekday:
        day_every = 7
    elif weekday_rand > weekday:
        if weekday == 5:
            day_every = 5 - weekday + random.randint(6, 7)
        else:
            day_every = weekday_rand - weekday

    number = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month']), year=int(json_output['DATE']['year']))
    day = number.day
    month = number.month
    year = number.year
    json_output['DATE']['day'] = day
    json_output['DATE']['month'] = month
    json_output['DATE']['year'] = year


def through_time_def(res, now, json_output):
    if ('after' in res) or ('every' in res) or ('time_range' in res):
        if "amount" in res:
            if res["amount"] == '':
                if 'every' in res:
                    res["amount"] = 1
                    json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + res["time_range"]
                elif ('after' in res):
                    res["amount"] = 1
        else:
            res["amount"] = 1

        if (find_dict_match(res["time_range"], time_measure) == 'minutes'):
            datetime_after = now.replace(hour=int(json_output['DATE']['hour']), minute=int(json_output['DATE']['minute'])) + datetime.timedelta(minutes=int(res["amount"]))
            json_output['DATE']['minute'] = datetime_after.minute
            json_output['DATE']['hour'] = datetime_after.hour
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["time_range"]

        elif find_dict_match(res["time_range"], time_measure) == 'hours':
            datetime_after = now.replace(hour=int(json_output['DATE']['hour'])) + datetime.timedelta(hours=int(res["amount"]))
            json_output['DATE']['hour'] = datetime_after.hour
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["time_range"]

        elif find_dict_match(res["time_range"], time_measure) == 'days':
            datetime_after = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month'])) + datetime.timedelta(days=int(res["amount"]))
            json_output['DATE']['day'] = datetime_after.day
            json_output['DATE']['month'] = datetime_after.month
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["time_range"]

        elif find_dict_match(res["time_range"], time_measure) == 'weeks':
            datetime_after = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month'])) + datetime.timedelta(weeks=int(res["amount"]))
            json_output['DATE']['day'] = datetime_after.day
            json_output['DATE']['month'] = datetime_after.month
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["g"]

        elif (find_dict_match(res["time_range"], time_measure) == 'months'):

            datetime_after = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month'])) + datetime.timedelta(days=30 * int(res["amount"]))
            json_output['DATE']['day'] = datetime_after.day
            json_output['DATE']['month'] = datetime_after.month
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["time_range"]

        elif find_dict_match(res["time_range"], time_measure) == 'years':
            json_output['DATE']['year'] += int(res["amount"])
            if 'every' in res:
                json_output['PARAMS']['repeat_every'] = res["every"] + ' ' + str(res["amount"]) + ' ' + res["time_range"]

        elif find_dict_match(res["time_range"], time_measure) == 'day':
            datetime_after = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month']), year=int(json_output['DATE']['year'])) + datetime.timedelta(days=30)
            json_output['DATE']['day'] = int(res["amount"])
            json_output['DATE']['month'] = datetime_after.month
            json_output['DATE']['year'] = datetime_after.year


def days_of_week_def(res, now, json_output):
    weekday = now.weekday()
    day_every = 0
    if find_dict_match(res["days_of_week"], days_of_weeks) < int(weekday):
        day_every = find_dict_match(res["days_of_week"], days_of_weeks) - weekday + 7
    elif find_dict_match(res["days_of_week"], days_of_weeks) == weekday:
        day_every = 7
    elif find_dict_match(res["days_of_week"], days_of_weeks) > weekday:
        if weekday == 5:
            day_every = 5 - weekday + random.randint(6, 7)
        else:
            day_every = find_dict_match(res["days_of_week"], days_of_weeks) - weekday
    number = now.replace(day=int(json_output['DATE']['day']), month=int(json_output['DATE']['month'])) + datetime.timedelta(days=day_every, weeks=0)
    json_output['DATE']['day'] = number.day
    json_output['DATE']['month'] = number.month


def part_of_day_def(res, json_output):
    if (res['part_of_day'] == 'с утра') or (res['part_of_day'] == 'утром'):
        json_output['DATE']['hour'] = random.randint(6, 11)
    elif (res['part_of_day'] == 'днём') or (res['part_of_day'] == 'днем'):
        json_output['DATE']['hour'] = random.randint(12, 17)
    elif res['part_of_day'] == 'вечером':
        json_output['DATE']['hour'] = random.randint(18, 23)
    elif res['part_of_day'] == 'ночью':
        json_output['DATE']['hour'] = random.randint(0, 5)
    json_output['DATE']['minute'] = '00'


def main_handler(message):
    global json_output
    res, matches = parse_message(message)

    task = str(get_task(message, matches)).strip().capitalize()

    status = SUCCESS
    if task is None:
        status = FAILED
    else:
        repeat_every = None

        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        day = now.day
        month = now.month
        year = now.year

        json_output = {'STATUS': status, 'TEXT': task,
                       'PARAMS': {'repeat_every': repeat_every},
                       'DATE': {'hour': hour, 'minute': minute, 'day': day, 'month': month, 'year': year}}

        if ('days_of_week' in res):
            days_of_week_def(res, now, json_output)

        if ('hours' and 'minutes') in res:
            json_output['DATE']['hour'] = res['hours']
            json_output['DATE']['minute'] = res['minutes']

        if 'month' in res:
            json_output['DATE']['month'] = find_dict_match(res["month"], months)
            json_output['DATE']['day'] = res['day']

        if 'relative' in res:
            relative_def(res, json_output)

        if ('week_weekend' or 'time_range') in res:
            week_weekend_def(res, json_output)

        if ('after' in res) or ('every' in res) or ('time_range' in res):
            through_time_def(res, now, json_output)

        if 'year' in res:
            json_output['DATE']['year'] = res['year']

        if 'part_of_day' in res:
            part_of_day_def(res, json_output)

    return json_output


for message in examples:
    print(f"\nКогда и о чем Вам напомнить, {user_name}?")
    res, matches = parse_message(message)
    task = get_task(message, matches)

    highlight_message(message, matches, end=' ')

    print(res)
    print("MESSAGE =", main_handler(message))

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()