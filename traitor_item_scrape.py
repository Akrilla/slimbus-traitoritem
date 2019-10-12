from lxml import html
import requests
import json
from collections import defaultdict
import time
import pprint
import concurrent.futures

# Free to edit - how many pages to work through.
pages_to_parse = 5

# Script vars
start = time.time()
total_rows_parsed = 0
round_traitor_ids = []
page_numbers = []
traitor_items = defaultdict(int)
current_page = 1

for i in range(1, pages_to_parse + 1):
    page_numbers.append(i)


def parse_round(traitor_round_id):
    start_request_time = time.time()
    round_page = requests.get("https://sb.atlantaned.space/rounds/" + traitor_round_id + "/traitor_uplink_items_bought")
    print("Time taken for request: " + str(time.time() - start_request_time))

    round_tree = html.fromstring(round_page.content)

    traitor_items_json_raw = round_tree.xpath('//*[@id="container"]/dl/dd[6]/pre/text()')

    if traitor_items_json_raw:
        traitor_items_json_raw = traitor_items_json_raw[0].strip()
        items_json = json.loads(traitor_items_json_raw)

        for item_name in items_json['data']:
            traitor_items_bought = items_json['data']
            quantity = 0
            for value in traitor_items_bought[item_name].values():
                quantity = value

            traitor_items[item_name] += quantity

    print("Round " + str(traitor_round_id) + " parsed.")


def parse_pages(current_page):
    page = requests.get("https://sb.atlantaned.space/rounds/page/" + str(current_page))
    tree = html.fromstring(page.content)

    page_round_rows = tree.xpath('//tbody//tr')

    for row in page_round_rows:
        round_id = row.xpath('./td[1]/a/i/following-sibling::text()')[0].strip()
        mode = row.xpath('./td[2]/i/following-sibling::text()')[0].strip()

        if "traitor" in str.lower(mode):
            round_traitor_ids.append(round_id)


print("Starting...")

# Can play with these numbers to not kill the site - more tends to just dos it.
executor = concurrent.futures.ThreadPoolExecutor(10)
futures = [executor.submit(parse_pages, page_number) for page_number in page_numbers]
concurrent.futures.wait(futures)

print("Parsed pages...")

# Can play with these numbers to not kill the site - more tends to just dos it.
executor = concurrent.futures.ThreadPoolExecutor(4)
futures = [executor.submit(parse_round, single_traitor_round_id) for single_traitor_round_id in round_traitor_ids]
concurrent.futures.wait(futures)

print('---')
print("Total traitor rounds parsed: " + str(len(round_traitor_ids)))
print('---')

# logFile = open('c:\\users\\akrilla\\desktop\\output'+'.txt', 'w')

pp  = pprint.PrettyPrinter(indent=4, stream=logFile)
pprint.sorted = lambda x, key=None: x

pp.pprint(dict(sorted(traitor_items.items(), key=lambda k_v: k_v[1], reverse=True)))

total_time = time.time() - start

print("Time taken: " + str(total_time))
print("Requests per second: " + str(len(round_traitor_ids) / total_time))
