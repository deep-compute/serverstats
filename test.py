#!/usr/bin/env python

import doctest
import unittest

import serverstats

suite = doctest.DocTestSuite(serverstats)

if __name__ == "__main__":
    doctest.testmod(serverstats)
