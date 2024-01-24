import json
import pendulum
import sys
from rich.console import Console

filepath = sys.argv[1]
with open(filepath) as f:
    data = json.load(f)
    f.close()

base_type_list = ['spotting', 'period']
measurements = []
for i in data:
    type = i['type']
    if type in base_type_list:
        data = {
            'date': i['date'],
            'type': i['type'],
            'option': i['value']
        }
        measurements.append(data)

cycles = []
current_cycle = []
prev_day = None

for i in measurements:
    day = pendulum.from_format(i['date'], 'YYYY-MM-DD')
    if prev_day == None:
        prev_day = day
    diff = prev_day.diff(day).days
    if diff > 5:
        # 'spotting' is taken into view if it is inside a period with 'period'
        if 'period' not in [i['type'] for i in current_cycle]:
            current_cycle.clear()
        if current_cycle:
            cycles.append(current_cycle[:])
            current_cycle.clear()
    current_cycle.append(i)
    prev_day = day

console = Console()
prev_first_day = None
for i in cycles:
    first_day = pendulum.from_format(i[-1]['date'], 'YYYY-MM-DD')
    if prev_first_day is None:
        prev_first_day = first_day
        continue

    diff = prev_first_day.diff(first_day, True).days
    cycle_len = diff + 1
    last_day = first_day.add(days=diff-1)

    last_period_day = pendulum.from_format(i[0]['date'], 'YYYY-MM-DD')
    period_len = first_day.diff(last_period_day, True).days + 1

    prev_first_day = first_day

    d = 'days'
    legend_cycle = f'[blue]{cycle_len} {d}[/] [black]{first_day.to_formatted_date_string(
    )} - {last_day.to_formatted_date_string()}[/]'
    if period_len == 1:
        d = 'day'
    legend_period = f'[black]{period_len} {d}[/]'
    legend_period = legend_period.ljust(17, " ")
    char = "❚"
    char_str = f'[red]{char * period_len}[/]{char * (cycle_len - period_len)}'

    console.print(f'{legend_cycle}\n {legend_period}{char_str}\n')
