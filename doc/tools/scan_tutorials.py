#!/usr/bin/env python

from pathlib import Path
import re

# Tasks
# 1. Find all tutorials
# 2. Generate tree (@subpage)
# 3. Check prev/next nodes

class Tutorial(object):
    def __init__(self, path):
        self.path = path
        self.title = None # doxygen title
        self.children = [] # ordered titles
        self.prev = None
        self.next = None
        with open(path, "rt") as f:
            self.parse(f)

    def parse(self, f):
        rx_title = re.compile(r"\{#(\w+)\}")
        rx_subpage = re.compile(r"@subpage\s+(\w+)")
        rx_prev = re.compile(r"@prev_tutorial\{(\w+)\}")
        rx_next = re.compile(r"@next_tutorial\{(\w+)\}")
        for line in f:
            if m := rx_title.search(line):
                if self.title is None:
                    self.title = m.group(1)
                    continue
            if m := rx_prev.search(line):
                if self.prev is None:
                    self.prev = m.group(1)
                    continue
            if m := rx_next.search(line):
                if self.next is None:
                    self.next = m.group(1)
                    continue
            if m := rx_subpage.search(line):
                self.children.append(m.group(1))
                continue

    def verify_prev_next(self, storage):
        res = True

        if self.title is None:
            print("[W] No title")
            res = False

        prev = None
        for one in self.children:
            c = storage[one]
            if c.prev is not None and c.prev != prev:
                print(f"[W] Wrong prev_tutorial: expected {c.prev} / actual {prev}")
                res = False
            prev = c.title

        next = None
        for one in reversed(self.children):
            c = storage[one]
            if c.next is not None and c.next != next:
                print(f"[W] Wrong next_tutorial: expected {c.next} / actual {next}")
                res = False
            next = c.title

        if len(self.children) == 0 and self.prev is None and self.next is None:
            print("[W] No prev and next tutorials")
            res = False

        return res

if __name__ == "__main__":

    p = Path('tutorials')
    print(f"Looking for tutorials in: '{p}'")

    all_tutorials = dict()
    for f in p.glob('**/*'):
        if f.suffix.lower() in ('.markdown', '.md'):
            t = Tutorial(f)
            all_tutorials[t.title] = t

    res = 0
    print(f"Found: {len(all_tutorials)}")
    print("------")
    for t in all_tutorials.values():
        if not t.verify_prev_next(all_tutorials):
            print(f"[E] Verification failed: {t.path}")
            print("------")
            res = 1

    exit(res)
