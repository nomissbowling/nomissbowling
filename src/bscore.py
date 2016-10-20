#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''bscore
'''

import sys, os

class bscore(object):
  def __init__(self):
    self.scores = []

  def msgbeep(self, msg):
    print msg
    if os.name != 'nt':
      import Tkinter
      r = Tkinter.Tk()
      r.bell()
      r.destroy()
      del r
    else:
      import winsound
      winsound.PlaySound('/windows/media/tada.wav', winsound.SND_FILENAME)
      winsound.MessageBeep(winsound.MB_ICONHAND) # winsound.MB_ICONEXCLAMATION)
      # winsound.Beep(880, 5)

  def parseFramestr(self, framestr):
    throws = list(framestr)
    if len(throws) == 0: return
    frame1 = 0
    while True:
      frames = []
      count = 0
      second = False
      frame = [0, 0, 0]
      for tr in throws[frame1:]:
        count += 1
        if tr == 'x':
          if second: raise Exception('x in second')
          frame[0] = 10
          frames.append(frame)
        elif tr == 'G':
          if second: raise Exception('G in second')
          frame[0] = 0
          second = True
        elif tr == '-':
          if not second: raise Exception('- in first')
          frame[1] = 0
          frames.append(frame)
          second = False
        elif tr == '/':
          if not second: raise Exception('/ in first')
          frame[1] = 10 - frame[0]
          frames.append(frame)
          second = False
        else:
          v = int(tr)
          if not second:
            frame[0] = v
            second = True
          else:
            frame[1] = v
            if frame[0] + frame[1] > 10: raise Exception('over 10')
            frames.append(frame)
            second = False
        if not second:
          f = len(frames)
          if f >= 10 and (frame[0] + frame[1] < 10): break
          if f >= 11 and (frames[9][0] < 10 or frames[10][0] < 10): break
          if f >= 12: break
          frame = [0, 0, 0]
      if second: frames.append(frame) # when the last 3rd throw is not x
      msg = '(frame1=%d) lost data at %dth frame'
      if len(frames) < 10:
        raise Exception(msg % (frame1, 10))
      if (frames[9][0] + frames[9][1] == 10 and len(frames) < 11):
        raise Exception(msg % (frame1, 11))
      if (frames[9][0] == 10 and frames[10][0] == 10 and len(frames) < 12):
        raise Exception(msg % (frame1, 12))
      self.scores.append(frames)
      if frame1 + count >= len(throws): break
      frame1 += 1 if frames[0][0] == 10 else 2

  def load(self, fname):
    print 'loading %s' % fname
    errors = 0
    ifp = open(fname, 'rb')
    for c, line in enumerate(ifp.readlines()):
      line = line.strip()
      if len(line) == 0: continue
      if line[0] == '#': continue
      framestr, cmt = line.split('#', 1)
      self.scores.append(cmt.decode('utf-8'))
      try:
        self.parseFramestr(''.join(framestr.split()))
      except Exception, e:
        errors += 1
        print 'in line %d:' % (c + 1), repr(e)
    ifp.close()
    if errors: self.msgbeep('%d error(s)' % errors)

  def vsc(self, sc, n):
    return sc[n] if len(sc) > n else [-1, -1, -1]

  def vtn(self, f, n):
    if n == 0: return 'x' if f[0] == 10 else ('G' if f[0] == 0 else f[0])
    else: return '/' if f[0] + f[1] == 10 else ('-' if f[1] == 0 else f[1])

  def calc(self, score):
    scorestr = []
    for c, f in enumerate(score):
      if c >= 10: break
      if c == 9: # 10th frame
        vsc_10 = self.vsc(score, 10) # 11th frame
        vsc_11 = self.vsc(score, 11) # 12th frame
        scorestr.append(' %s%s%s' % (
          'x' if f[0] == 10 else self.vtn(f, 0),
          'x' if f[0] == 10 and vsc_10[0] == 10 else (
            self.vtn(vsc_10, 0) if f[0] == 10 else self.vtn(f, 1)),
          'x' if f[0] == 10 and vsc_10[0] == 10 and vsc_11[0] == 10 else (
            self.vtn(vsc_11, 0) if f[0] == 10 and vsc_10[0] == 10 else (
              self.vtn(vsc_10, 1) if f[0] == 10 else (
                self.vtn(vsc_10, 0) if f[0] + f[1] == 10 else ' ')))))
      else:
        scorestr.append('  %s%s' % (
          ' ' if f[0] == 10 else self.vtn(f, 0),
          'x' if f[0] == 10 else self.vtn(f, 1)))
      f[2] = f[0] + f[1] + (score[c - 1][2] if c > 0 else 0)
      if f[0] == 10: f[2] += score[c + 1][0] + score[c + 1][1] + (
        score[c + 2][0] if score[c + 1][0] == 10 else 0)
      elif f[0] + f[1] == 10: f[2] += score[c + 1][0]
    scorestr.append('\n')
    for c, f in enumerate(score):
      if c >= 10: break
      scorestr.append(' %3d' % f[2])
    return ''.join(scorestr)

  def report(self):
    for score in self.scores:
      print score if not isinstance(score, list) else self.calc(score)

if __name__ == '__main__':
  bs = bscore()
  bs.load(os.path.join(os.path.abspath('.'), 'bscore.txt'))
  bs.report()
