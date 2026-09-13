@echo off
title UniKL Steganography Tool (IKB 21303)
echo ===============================================================
echo     UniKL MIIT - Cryptography and Steganography (IKB 21303)
echo            Image Steganography Suite (Assignment 2)
echo ===============================================================
echo Launching Steganography GUI Application...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred. Please make sure Python and required libraries are installed.
    echo Run: pip install pillow matplotlib numpy
    pause
)
