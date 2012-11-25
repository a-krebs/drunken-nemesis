#!/usr/bin/env python2.7
import bootstrap
import sys
import os

from multiprocessing.queues import Queue
from multiprocessing.pool import Pool
import multiprocessing
import itertools

from aisbx import platform
from game import application

def run(args):
    try:
        map, candidates = args
        sys.stderr.write('.')
        runner = platform.ConsoleRunner()
        app = application.CaptureTheFlag(list(candidates), map, quiet = True, games = 1)
        runner.run(app)
        sys.stderr.write('o')
        return map, app.scores
    except KeyboardInterrupt:
        return None 


if __name__ == '__main__':
    p = Pool(processes = multiprocessing.cpu_count())

    total = 0
    scores = {}
    commanders = ['examples.Greedy', 'examples.Balanced', 'examples.Random', 'examples.Defender']
    maps = ['map00', 'map01', 'map10', 'map20']

    pairs = itertools.permutations(commanders, 2)
    games = list(itertools.product(maps, pairs))

    print "Running competition with %i commanders and %i maps, for a total of %i games.\n" % (len(commanders), len(maps), len(games))
    try:
        for map, results in p.map(run, games):
            for bot, score in results.items():
                scores.setdefault(bot, [0, 0])
                scores[bot][0] += score[0]
                scores[bot][1] += score[1]
            total += 1
    except KeyboardInterrupt:
        print "\nTerminating competition due to keyboard interrupt."
        p.terminate()
        p.join()
    else:
        print "\n%i total games run." % (total)
        for r, s in sorted(scores.items(), key = lambda i: -i[1][0]+i[1][1]):
            print "{}   for: {}, against: {}".format(r.replace('Commander', '').upper(), s[0], s[1])
        raw_input()

