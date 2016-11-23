#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''cs_toicon
image[.png/.bmp/.ico/etc] to masked .ico
inspired http://d.hatena.ne.jp/rsky/20070919/1190163713
'''

import sys, os
from PIL import Image
from cStringIO import StringIO
from struct import pack, unpack

def toicon(infile, outfile=None, dim=(32, 32), mp=(0, 0)):
  width, height = dim
  if width < 1 or width > 256 or height < 1 or height > 256:
    raise ValueError('invalid dim')
  im = Image.open(infile)
  sys.stderr.write('original: %s %s %s\n' % (im.format, im.size, im.mode))
  # tmp = im.copy() # save original
  im = im.convert('P', palette=Image.ADAPTIVE, colors=256,
    dither=Image.FLOYDSTEINBERG) # BGRA pal[0] will be ffffff00 when used white
  # im.thumbnail(dim, Image.BICUBIC) # (fast) expect palette 256 colors
  im.thumbnail(dim, Image.ANTIALIAS) # (slow) colors will be changed ?
  width, height = im.size
  sys.stderr.write('thumbnail: %s %s %s\n' % (im.format, im.size, im.mode))
  # pal = im.getpalette()
  # pal[] = ... # adjust palette
  # im.putpalette(pal)
  # dat = list(im.getdata())
  # dat[] = ... # adjust palette number
  # im.putdata(dat)
  bmp = StringIO()
  im.save(bmp, 'BMP')
  image_size = bmp.tell() - 14 # 3368
  # adjust src bytes per line
  wlen = width # 1pixel=8bpp
  # adjust mask bytes per line
  if False:
    blen = ((width + 31) / 32) * 4 # 1pixel=1bit
  else:
    if False: blen = width * 3 # 1pixel=24bit
    else: blen = (width + 7) / 8 # 1pixel=1bit
    if blen % 4: blen += 4 - blen % 4 # needs 4bytes alignment
  mask_size = blen * height # 384=8x48
  sys.stderr.write('%d (%d) (%d) %d\n' % (image_size, wlen, blen, mask_size))
  ico = StringIO()
  ico.write(pack('<3H', 0, 1, 1)) # (0), (1:ICO, 2:CUR), (N:number of images)
  ico.write(pack('<BBBBHHII',
    width & 255, # bWidth
    height & 255, # bHeight
    0, # bColorCount (0:8bpp, N:number of colors)
    0, # bReserved (must be 0)
    1, # wPlanes
    24, # wBitCount
    image_size + mask_size, # dwBytesInRes
    6 + 16)) # dwImageOffset (6=<3H, 16=<BBBBHHII)
  bmp.seek(14) # skip BITMAPFILEHEADER
  ico.write(bmp.read(8)) # icHeader part BITMAPINFOHEADER (biSize, biWidth)
  ico.write(pack('<I', height * 2)) # combined height of the XOR and AND masks
  bmp.seek(4, 1) # part BITMAPINFOHEADER (biHeight)
  ico.write(bmp.read(28)) # remain BITMAPINFOHEADER (biPlanes...biClrImportant)
  if False:
    biClrUsed = 256
  else:
    bmp.reset()
    bf = bmp.read(14) # BITMAPFILEHEADER
    bi = bmp.read(8 + 4 + 28) # BITMAPINFOHEADER
    bfType, bfSize, bfReserved1, bfReserved2, bfOffBits = unpack('<HIHHI', bf)
    biSize, biWidth, biHeight, biPlanes, biBitCount, biCompression, \
      biSizeImage, biXPPM, biYPPM, biClrUsed, biClrImportant \
        = unpack('<IIIHHIIIIII', bi)
    sys.stderr.write('%04x %08x (%04x %04x) %08x\n' % (
      bfType, bfSize, bfReserved1, bfReserved2, bfOffBits))
    sys.stderr.write('%08x %08x %08x %04x %04x %08x\n' % (
      biSize, biWidth, biHeight, biPlanes, biBitCount, biCompression))
    sys.stderr.write('%08x %08x %08x %08x %08x\n' % (
      biSizeImage, biXPPM, biYPPM, biClrUsed, biClrImportant))
  pal = ''
  if biClrUsed:
    pal = bmp.read(4 * biClrUsed) # palette 256 x 4 BGRA
    ico.write(pal) # icColors
    for y in range(64):
      q = y * 16
      sys.stderr.write('%04x:' % q)
      for x in range(4):
        for z in range(4):
          sys.stderr.write(' %02x' % ord(pal[q + x * 4 + z]))
        sys.stderr.write(' ')
      sys.stderr.write('\n')
  img = bmp.read() # len(img)=2304=48x48
  ico.write(img) # icXOR
  c, r = mp
  if c < 0: c = 0
  if c >= width: c = width - 1
  if r < 0: r = 0
  if r >= height: r = height - 1
  mpal = ord(img[r * wlen + c])
  sys.stderr.write('(%d, %d) mask pal: %02x [%04x]\n' % (c, r, mpal, 4 * mpal))
  if len(pal):
    for h in range(height):
      for w in range(blen): # bytes per line
        b = 0
        if w * 8 < wlen:
          p = h * wlen + w * 8
          for m in range(8): # bits
            b |= (0x01 << (7 - m)) if ord(img[p + m]) == mpal else 0
        ico.write(chr(b)) # icAND
  else:
    ico.write('\0' * mask_size) # icAND
  ico.reset()
  if outfile: open(outfile, 'wb').write(ico.read())
  else: return ico.read()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s infile\n' % sys.argv[0])
  else:
    infile = sys.argv[1]
    name, ext = os.path.splitext(os.path.basename(infile))
    outfile = '%s.ico' % name
    toicon(infile, outfile, (48, 48), (47, 47))
    print Image.open(outfile).size
