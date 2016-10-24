#!/usr/bin/env python3

from tabulate import tabulate
from collections import Counter, namedtuple
from sys import argv
import hw7 as hw

# given two correspondence sets, return merge unknowns if possible
def try_merge_similar(xs, ys, unknown='-'):

    # they're not 'similar' if they're the same
    if xs == ys:
        return False
    
    # they can't be similar if neither is ambiguous
    if '-' not in xs + ys:
        return False

    merged = []
    for x, y in zip(xs.split(), ys.split()):

        if x == y:
            merged.append(x)
            continue

        if unknown not in (x, y):
            return False

        # one is unknown, other is not
        merged.append(x if y == unknown else y)

    return ' '.join(merged)

def collapse(d):
    collapsed = dict()

    # for each sound correspondence set
    for num, phonesets in d.items():
        for phoneset in phonesets:

            # check for an identical match
            if phoneset in collapsed:
                collapsed[phoneset].append(num)
                continue

            # check for a partial match
            merge = False
            for k in collapsed:
                merge = try_merge_similar(phoneset, k)
                if merge:
                    nums = collapsed[k][:]
                    del collapsed[k]
                    collapsed[merge] = nums
                    collapsed[merge].append(num)
                    break
            if merge:
                continue

            # no match found
            collapsed[phoneset] = list()
            collapsed[phoneset].append(num)

    return collapsed

def hlsort(d) -> [('a b c d', [1, 2, 3, 4])]:

    # { phone: (count of phone, soundset, instances) }
    soundsets_by_phone = dict()

    SSInfo = namedtuple('SSInfo', 'count soundset instances'.split())

    # group soundsets by most common phone
    for soundset, instances in d.items():
        most_common, count = Counter(soundset.split()).most_common(1)[0]
        v = SSInfo(count, soundset, instances)
        try:
            soundsets_by_phone[most_common].append(v)
        except KeyError:
            soundsets_by_phone[most_common] = [v]

    out = []
    for phone in sorted(soundsets_by_phone.keys()):
        soundsets = soundsets_by_phone[phone]

        # least priority: earliest instance in dataset
        soundsets.sort(key=lambda x: x.instances[0])

        # second priority: most instances in dataset
        soundsets.sort(key=lambda x: len(x.instances), reverse=True)

        # top priority: most of the most common phone
        soundsets.sort(key=lambda x: x.count, reverse=True)

        out.extend([ (x.soundset, x.instances) for x in soundsets ])

    return out

def latex_print(table, languages):
    print('\\usepackage{booktabs}\n\\begin{table}[ht]\n\\begin{centering}')
    print(tabulate(table, tablefmt='latex_booktabs', headers=headers))
    print('\\end{centering}\n\\end{table}')

def sep_print():
    print('', '-' * 80, '', sep='\n')

def flat_print(table, headers):
    for soundset in [headers] + table:
        print(*soundset, sep='\t')

table = hlsort(collapse(hw.sets))
table = [ [str(i + 1) + '.'] + sounds.split() + [','.join(map(str, nums))]
          for i, (sounds, nums) in enumerate(table) ]

headers = [''] + [ x[:2] for x in hw.languages ] + ['gloss']

if not argv[1:]:
    flat_print(table, headers)

if '-l' in argv[1:]:
    latex_print(table, headers)
