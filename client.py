#!/usr/bin/env python

import concurrent.futures
import requests
import argparse
import time
import urllib3
import json

requests.packages.urllib3.disable_warnings()

def worker_get(opt):
    url, data = opt.url, opt.post_data
    try:
        ret = requests.get(url, verify=False)
        msg = True
    except Exception as e:
        ret = -1
        msg = str(e)
    return (ret, msg)

def worker_post(opt):
    url = opt.url
    data = json.dumps(opt.post_data, ensure_ascii=False).encode()
    headers = { "application": "json" }
    try:
        ret = requests.post(url, data=data, headers=headers, verify=False)
        msg = True
    except Exception as e:
        ret = -1
        msg = str(e)
    return (ret, msg)

# do requests.
cftp = concurrent.futures.ThreadPoolExecutor
cfpp = concurrent.futures.ProcessPoolExecutor

def exec_thread_pool(nb_threads):
    with cftp(max_workers=nb_threads) as ex:
        for ret in ex.map(worker, [opt for _ in range(nb_threads)]):
            results.append(ret)

def split_even(nb_items: int, nb_slots: int) -> list:
    """
    items_per_slot: a list of slots containing items splitted evenly.
    e.g. (nb_items, nb_slots) = (5, 3) -> items_per_slot = [2, 2, 1]
    """
    items_per_slot = []
    if nb_slots == 0:
        return items_per_slot
    even_n = nb_items // nb_slots
    for i in range(nb_slots):
        items_per_slot.append(even_n)
    rest_n = nb_items % nb_slots
    if rest_n > 0:
        for i in range(nb_slots):
            items_per_slot[i] += 1
            if rest_n == 1:
                break
            rest_n -= 1
    return items_per_slot

# set options
ap = argparse.ArgumentParser()
ap.add_argument("url", action="store",
                help="specify the URL.")
ap.add_argument("-p", action="store", dest="post_data_file",
                help="specify data to post.")
ap.add_argument("--nb-reqs", action="store", dest="nb_reqs",
                type=int, default=1,
                help="specify the number of requests.")
ap.add_argument("--nb-procs", action="store", dest="nb_procs",
                type=int, default=1,
                help="specify the number of processes. "
                    "default is 1 process handles all requests.")
opt = ap.parse_args()

if opt.post_data_file:
    worker = worker_post
    opt.post_data = json.loads(open(opt.post_data_file).read())
else:
    worker = worker_get

threads_per_proc = split_even(opt.nb_reqs, opt.nb_procs)
print(threads_per_proc)

results = []

t_start = time.time()
if opt.nb_procs == 1:
    exec_thread_pool(opt.nb_reqs)
else:
    # opt.nb_proc > 1
    with cfpp(max_workers=len(threads_per_proc)) as ex:
        for ret in ex.map(exec_thread_pool, [n for n in threads_per_proc]):
            results.append(ret)
t_end = time.time()

# print result.
for i in range(len(results)):
    print("{}: {}".format(1+i,results[i]))

print(t_end - t_start)
