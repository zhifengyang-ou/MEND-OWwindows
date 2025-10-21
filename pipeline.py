import os
import shutil
import sys
from datetime import datetime

now_string = str(datetime.now())
comment = sys.argv[1]

filename = 'MEND_namelist.nml'
#filename2 = 'FBEM_namelist.nml'
folder = ''

with open(filename, 'r') as file:
    for line in file:
        line = line.strip()
        if 'Dir_Output  = ' in line:
            folder = line.split('=')[1].strip().replace("'", '').replace('/', '\\')

if folder:
    os.makedirs(folder, exist_ok=True)

logfile = 'log.txt'
with open(logfile, 'r') as log_file, open(os.path.join(folder, logfile), 'w') as output_file:
    for line in log_file:
        output_file.write(line)

with open(os.path.join(folder, logfile), 'a') as output_file:
    output_file.write(folder + '\n')
    output_file.write(now_string + '\n')

shutil.copy(os.path.join(folder, logfile), 'log.txt')
with open(os.path.join(folder, 'comment.txt'), 'w') as comment_file:
    comment_file.write(comment)

shutil.copy(filename, os.path.join(folder, 'MEND_namelist.nml'))
#shutil.copy(filename2, os.path.join(folder, 'FBEM_namelist.nml'))
# File paths with backslashes for Windows
FSRCS = [
    r"src\MOD_MEND_TYPE.F90",
    r"src\MOD_OPT_TYPE.F90",
    r"src\MOD_USRFS.F90",
    r"src\MOD_STRING.F90",
    r"src\MOD_MEND.F90",
    r"src\MOD_MCMC.F90",
    r"src\MOD_OPT.F90",
    r"src\MEND_IN.F90",
    r"src\MEND_main.F90"
]

CPPFLAGS = ''

# Compile Fortran files
os.system(f"gfortran.exe {' '.join(FSRCS)} {CPPFLAGS} -o run.exe")

# Execute the compiled program
os.system("run.exe")

# Remove the compiled executable
#os.remove("nws.exe")

# Remove .mod files
for filename in os.listdir():
   if filename.endswith(".mod"):
      os.remove(filename)

