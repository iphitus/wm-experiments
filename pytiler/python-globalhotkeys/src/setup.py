from distutils.core import setup, Extension
import commands

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw



setup(name = "globalhotkeys",
      version = "1.0",
      ext_modules = [Extension("globalhotkeys", 
                ["globalhotkeys.c", "eggaccelerators.c", "keybinder.c"], 
                **pkgconfig("glib-2.0","gtk+-2.0")) ])

