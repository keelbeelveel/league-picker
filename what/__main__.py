import helper
helper.run()

import sys
import picker
import stat_loader
import os

if len(sys.argv) == 1 or sys.argv[1] != "edit":
    picker.select(sys.argv[1:])

elif sys.argv[1] == "edit":
    stat_loader.run()

