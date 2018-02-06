#!/usr/bin/env python

import doctest

from serverstats import serverstats

suite = doctest.DocTestSuite(serverstats)

if __name__ == "__main__":
    doctest.testmod(serverstats)
