import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    '--name=%s' % "Class Helper",
    '--onefile',
    '--windowed',
    '--add-data=%s' % os.path.join('img', 'toolbox.png', 'img'),
    '--icon=%s' % os.path.join('img', 'toolbox.ico', 'img'),
    os.path.join('classhelper.py'),
])
