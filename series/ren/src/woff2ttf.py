import sys
from fontTools.ttLib import TTFont
src, dst = sys.argv[1], sys.argv[2]
f = TTFont(src)
f.flavor = None
f.save(dst)
print("ok", dst)
