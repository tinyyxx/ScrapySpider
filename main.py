# -*- coding: utf-8 -*-

__author__ = 'Leo'

from scrapy.cmdline import execute
import sys
import os

from openpyxl import Workbook
from openpyxl.compat import range


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "auctionSpider"])
