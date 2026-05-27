import os
import sys

def resource_path(relative_path):
    base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.')
    return os.path.join(base, relative_path)

GURU_JPG = resource_path('guru.jpg')