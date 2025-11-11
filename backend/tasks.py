import os
from huey import SqliteHuey
from random import randint as rd
import time
import subprocess
# Initialize Huey
huey = SqliteHuey(filename='task.db')

@huey.task()
def sleepRand():
    n = rd(5, 20)
    print(f"Sleeping for {n} seconds...")
    time.sleep(n)
    print("Task complete!")


@huey.task()
def print_pdf(filepath, printer_name=None):
    """
    Prints a PDF file using SumatraPDF in silent mode.
    
    Args:
        filepath (str): Full path to the PDF file.
        printer_name (str, optional): Name of the printer. If None, default printer is used.
    """
    # Path to SumatraPDF executable — change if installed elsewhere
    sumatra_path = r"C:\Users\James Jessica\AppData\Local\SumatraPDF\SumatraPDF.exe"
    
    # Ensure the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF not found: {filepath}")

    # Build command
    cmd = [sumatra_path, "-print-to-default", "-silent", filepath]
    
    if printer_name:
        cmd = [sumatra_path, f"-print-to", printer_name, "-silent", filepath]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Printed: {os.path.basename(filepath)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Printing failed: {e}")
    except Exception as e:
        print(f"⚠️ Error: {e}")



