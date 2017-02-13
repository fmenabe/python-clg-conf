# coding: utf-8

# Trick for bypassing the limitation in python 2.7 that replace imports by None
# when replacing the current module by an object (http://stackoverflow.com/questions/
# 29107470/imported-modules-becomes-none-when-replacing-current-module-in-sys-modules-using).
import sys
from .src import Config
sys.modules[__name__] = Config()
