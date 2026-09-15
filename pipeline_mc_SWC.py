import os
import shutil
import sys
from datetime import datetime

# Grab comment from command line, or set a default
comment = sys.argv[1] if len(sys.argv) > 1 else "Batch MC Run - All Treatments"

filename = 'MEND_namelist.nml'
num_simulations = 100 
treatments = ["UC", "UW", "CC", "CW"]
base_dir = os.path.abspath(os.getcwd())

# ---------------------------------------------------------
# Define the specific Pinitial values for each treatment
# ---------------------------------------------------------
pinitial_params = {
    "CC": "0.90000000,     0.10000000,     0.09843100,     0.20000000,    80.00000000,    65.40000000,     9.10000000,   500.00000000,     3.50000000,     8.61000000,     0.00330400,     0.00010392,     0.00331854,     2.00000000,     0.15000000,     0.10000000,     0.00100486,     0.20000000,     0.00168533,     0.45000000,     0.00102087,     2.00000000,     4.50000000,     0.00100000,     0.05280551,     0.39000000,     1.00000000,     0.00054158,     0.00100000,     0.00100000,     0.06727696,     0.59019373,     0.09915267,     8.18354009,     0.10000000,     0.01000000,     0.01000000,     0.01000000,     0.00001000,     0.01000000,     0.00922395,     0.05000000,     0.50000000,     0.00010000,   100.00000000,     0.00000500,     0.00100000",
    "CW": "0.90000000,     0.10000000,     0.10690000,     0.21578316,    80.00000000,    65.40000000,     9.10000000,   500.00000000,     3.50000000,     8.61000000,     0.00330400,     0.00010923,     0.00417802,     2.00000000,     0.15000000,     0.10000000,     0.00139062,     0.20000000,     0.00052709,     0.45000000,     0.00107660,     2.00000000,     4.50000000,     0.00100000,     0.01995590,     0.39000000,     1.00000000,     0.00014852,     0.00100000,     0.00442256,     0.07378253,     0.39041564,     0.09999437,     7.25634807,     0.10000000,     0.01000000,     0.01000000,     0.01000000,     0.00001000,     0.01000000,     0.01000000,     0.05000000,     0.50000000,     0.00010000,   100.00000000,     0.00000500,     0.00100000",
    "UC": "0.90000000,     0.10000000,     0.18380000,     0.35000000,    80.00000000,    65.40000000,     9.10000000,   500.00000000,     3.50000000,     8.61000000,     0.00330400,     0.00010130,     0.00150000,     2.00000000,     0.15000000,     0.10000000,     0.00165228,     0.20000000,     0.00158316,     0.45000000,     0.01516757,     2.00000000,     4.50000000,     0.00100000,     0.23751548,     0.39000000,     1.00000000,     0.00054731,     0.00100000,     0.00100000,     0.04644759,     0.48951936,     0.03207429,     9.97907547,     0.10000000,     0.01000000,     0.01000000,     0.01000000,     0.00001000,     0.01000000,     0.00101031,     0.05000000,     0.50000000,     0.00010000,   100.00000000,     0.00000500,     0.00100000",
    "UW": "0.90000000,     0.10000000,     0.20085450,     0.40000000,    80.00000000,    65.40000000,     9.10000000,   500.00000000,     3.50000000,     8.61000000,     0.00330400,     0.00010059,     0.00136022,     2.00000000,     0.15000000,     0.10000000,     0.00100345,     0.20000000,     0.00514636,     0.45000000,     0.01552098,     2.00000000,     4.50000000,     0.00100000,     0.59108091,     0.39000000,     1.00000000,     0.00056449,     0.00100000,     0.00100000,     0.03837325,     0.62499314,     0.09912387,     6.00866494,     0.10000000,     0.01000000,     0.01000000,     0.01000000,     0.00001000,     0.01000000,     0.00569471,     0.05000000,     0.50000000,     0.00010000,   100.00000000,     0.00000500,     0.00100000"
}

# ---------------------------------------------------------
# 1. Compile Fortran files ONCE to save processing time
# ---------------------------------------------------------
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

print("Compiling Fortran executable...")
# ---------------------------------------------------------
# 1. Aggressive Compilation Block (Runs ONCE)
# ---------------------------------------------------------
if comment == "fast" and os.path.exists("run.exe"):
    print("⚡ 'fast' mode enabled: Skipping compilation, using existing run.exe.")
else:
    # Aggressive optimization flags
    OPTFLAGS = "-O3 -march=native -funroll-loops"
    MATH_TUNE = "-ffast-math -fassociative-math -freciprocal-math -fno-signed-zeros"
    F90_FLAGS = "-fallow-argument-mismatch -fimplicit-none"
    CPPFLAGS = "-cpp"

    # Set up absolute paths
    build_dir = os.path.join(base_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    # Move INTO the build directory to bypass the gfortran -J relative path bug
    os.chdir(build_dir)

    object_files = []
    print("🚀 Starting maximum-optimization build...")
    
    for src_file in FSRCS:
        # Navigate up one level from 'build' to reach the source files
        rel_src_file = os.path.join("..", src_file).replace('\\', '/')
        base_name = os.path.basename(src_file)
        obj_file = base_name.replace('.F90', '.o')
        
        # Notice we removed -J and -I flags because we are natively inside the build dir
        compile_cmd = (
            f"gfortran -c {rel_src_file} "
            f"{OPTFLAGS} {MATH_TUNE} {F90_FLAGS} {CPPFLAGS} "
            f"-o {obj_file}"
        )
        print(f"🔧 Compiling: {base_name}")
        if os.system(compile_cmd) != 0:
            print(f"❌ Compilation failed for {base_name}!")
            sys.exit(1)
        object_files.append(obj_file)

    # Link all object files and output the executable to the root directory
    link_cmd = (
        f"gfortran {' '.join(object_files)} {OPTFLAGS} -o ../run.exe "
        f"-static-libgcc -static-libgfortran"
    )
    print(f"🔗 Link command: {link_cmd}")
    if os.system(link_cmd) != 0:
        print("❌ Linking failed!")
        sys.exit(1)
        
    # Return to the root directory for the rest of the script
    os.chdir(base_dir)

# Read the original namelist into memory to act as a master template
with open(filename, 'r') as file:
    namelist_lines = file.readlines()

# ---------------------------------------------------------
# 2. Outer Loop: Iterate through each Treatment
# ---------------------------------------------------------
for trt in treatments:
    print(f"\n==================================================")
    print(f" STARTING BATCH SIMULATIONS FOR TREATMENT: {trt}")
    print(f"==================================================")

    # Fetch the correct initial parameters for this treatment
    current_pinitial = pinitial_params[trt]

    # ---------------------------------------------------------
    # 3. Inner Loop: Iterate through Monte Carlo files
    # ---------------------------------------------------------
    for i in range(1, num_simulations + 1):
        
        iter_str = f"{i:03d}"
        mc_filename = f"SWC_day_MC_{iter_str}.dat"
        
        # Define the dynamic paths for this specific treatment and iteration
        inp_folder = f"userio/inp_{trt}/"
        new_out_folder = f"userio/out_{trt}_MC_{iter_str}/"
        folder_path_win = new_out_folder.replace('/', '\\')

        print(f"--- Running {trt} | Sim {i}/{num_simulations} | File: {mc_filename} ---")

        # Update the namelist lines dynamically
        modified_lines = []
        for line in namelist_lines:
            # Strip whitespace to ensure exact matches
            clean_line = line.strip()
            
            if clean_line.startswith('sSite =') or clean_line.startswith('sSite='):
                modified_lines.append(f"    sSite = '{trt}'\n")
            elif clean_line.startswith('Dir_Input') and '=' in clean_line:
                modified_lines.append(f"    Dir_Input   = '{inp_folder}'\n")
            elif clean_line.startswith('Dir_Output') and '=' in clean_line:
                modified_lines.append(f"    Dir_Output  = '{new_out_folder}'\n")
            elif clean_line.startswith('sfilename_SM') and '=' in clean_line:
                modified_lines.append(f"    sfilename_SM = '{mc_filename}'\n")
            
            # This logic captures the master 'Pinitial = ' line but ignores 'Pinitial(1:2) ='
            elif clean_line.startswith('Pinitial') and '(' not in clean_line.split('=')[0]:
                # Appends the new parameters and adds the Fortran namelist closure '/' at the end
                modified_lines.append(f"    Pinitial = {current_pinitial} /\n")
            
            else:
                modified_lines.append(line)

        # Overwrite the namelist file with the new parameters
        with open(filename, 'w') as file:
            file.writelines(modified_lines)

        # Execute the pre-compiled program
        os.system("run.exe")

        # ---------------------------------------------------------
        # 4. Handle Logging and File Organization for this run
        # ---------------------------------------------------------
        os.makedirs(folder_path_win, exist_ok=True)
        logfile = 'log.txt'
        now_string = str(datetime.now())

        if os.path.exists(logfile):
            # Copy log into the new output folder
            with open(logfile, 'r') as log_file, open(os.path.join(folder_path_win, logfile), 'w') as output_file:
                for log_line in log_file:
                    output_file.write(log_line)

            # Append metadata to the copied log
            with open(os.path.join(folder_path_win, logfile), 'a') as output_file:
                output_file.write(folder_path_win + '\n')
                output_file.write(now_string + '\n')

            # Update the main directory log
            shutil.copy(os.path.join(folder_path_win, logfile), logfile)

        # Write comment file
        with open(os.path.join(folder_path_win, 'comment.txt'), 'w') as comment_file:
            comment_file.write(comment)

        # Save a copy of the exact namelist used for this iteration
        shutil.copy(filename, os.path.join(folder_path_win, 'MEND_namelist.nml'))

# ---------------------------------------------------------
# 5. Clean up the environment after ALL treatments finish
# ---------------------------------------------------------
print("\nCleaning up compiled files...")
if os.path.exists("run.exe"):
    os.remove("run.exe")

for f in os.listdir():
    if f.endswith(".mod"):
        os.remove(f)

print("Batch Monte Carlo simulations completed successfully for all treatments.")