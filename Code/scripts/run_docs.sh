#!/usr/bin/env bash
# run_docs.sh
# Generates HTML documentation from docstrings using Doxygen

echo "==========================================================="
echo " Generating HTML Software Documentation (Doxygen) "
echo "==========================================================="

# Ensure doxygen is installed
if ! command -v doxygen &> /dev/null
then
    echo "doxygen could not be found. Please install it."
    echo "Mac: brew install doxygen"
    echo "Linux: sudo apt-get install doxygen"
    exit 1
fi

echo "Building documentation..."
doxygen Doxyfile

echo "==========================================================="
echo " Documentation generated successfully in doxygen/html/"
echo " Open doxygen/html/index.html in your browser."
echo "==========================================================="
