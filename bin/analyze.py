from datetime import datetime, timedelta
import glob
import json
import sys
import os

import tabulate
import tqdm

file_name_offset = timedelta(hours=6)


def pp_json(data):
    return json.dumps(data, indent=True, sort_keys=True)


def pp_cal(date):
    return "{}-{:02d}-{:02d}".format(date.year, date.month, date.day)


def normalize_date(other_date):
    return datetime(
        year=other_date.year,
        month=other_date.month,
        day=other_date.day
    )


def parse_date(raw_date):
    date_format = "%Y%m%dT%H%M%SZ"
    parsed_date = datetime.strptime(raw_date, date_format)
    offset_date = parsed_date - file_name_offset
    return normalize_date(offset_date)


def iterate_files():
    paths = sorted(glob.glob('unzipped/*.json'))
    for path in paths:
        filename = os.path.basename(path)
        raw_date = filename.split('-')[0]
        date = parse_date(raw_date)

        yield path, date


def get_cheapest_price(itinerary):
    if itinerary['tariffModulation'] is not None:
        return itinerary['tariffModulation']['adultOneWayPrice']

    return itinerary['flexPrice']['adultOneWayPrice']


def pp_prices(data):
    absed = []
    for days_in_advance, price in data:
        pretty_price = '${}'.format(price)
        absed.append((abs(int(days_in_advance)), pretty_price))

    headers = ['Days in advance', 'Price']
    return tabulate.tabulate(absed, headers=headers, stralign="right")


def main():
    with open('index.json') as f:
        indexed_data = json.load(f)

    date = input('Enter a date in the format 2019-03-15: ')
    print('Here are all departure times for {}'.format(date))

    date_data = indexed_data[date]
    departure_times = sorted(date_data.keys())

    for index, departure_time in enumerate(departure_times):
        print(str(index + 1).rjust(2) + ': ' + departure_time)

    selection = None
    while selection != 'q':
        selection = int(input('\nEnter the desired itinerary: '))
        print()
        key = list(departure_times)[selection - 1]
        values = list(date_data[key].items())

        print('Showing results for trip leaving at {}\n'.format(key))
        print(pp_prices(values))


def parse_orleans_date(raw_date):
    date_format = '%Y-%m-%dT%H:%M:%S'
    return normalize_date(datetime.strptime(raw_date, date_format))


def index():
    all_data = {}
    for path, scrape_date in tqdm.tqdm(sorted(iterate_files())):
        with open(path) as f:
            scrape_data = json.load(f)

        for day_data in scrape_data:
            day = parse_orleans_date(day_data['date'])

            day_delta = round((scrape_date - day).days)
            day_key = pp_cal(day)

            if day_key not in all_data:
                all_data[day_key] = {}

            for itinerary in day_data['itineraries']:
                price = get_cheapest_price(itinerary)
                departure_time = itinerary['departureTime']

                if departure_time not in all_data[day_key]:
                    all_data[day_key][departure_time] = {}

                all_data[day_key][departure_time][day_delta] = price

    with open('index.json', 'w+') as f:
        f.write(json.dumps(all_data))


if __name__ == "__main__":
    if '--index' in sys.argv:
        index()
    else:
        main()
