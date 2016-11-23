#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''cs_utime
os.stat(fn).st_ctime # 978307200.0
tt=time.strptime('20010101T090000', '%Y%m%dT%H%M%S') # (2001,1,1,9,0,0,0,1,-1)
t=time.mktime(tt) # 978307200.0
os.utime(fn, (t, t)) # (atime, mtime)
'''

import sys, os, stat
import time

FSENC = 'cp932'
UPATH = u'/tmp/tmp'
FILES = [
  (u'f0.tsv', '20010101T090000'),
  (u'f1.tsv', '20010101T090000'),
  (u'f2.tsv', '20010101T090000')]

def set_ts(fn, ts):
  t = time.mktime(time.strptime(ts, '%Y%m%dT%H%M%S'))
  os.utime(fn, (t, t))

def main():
  for fn, ts in FILES: set_ts((u'%s/%s' % (UPATH, fn)).encode(FSENC), ts)

if __name__ == '__main__':
  main()
