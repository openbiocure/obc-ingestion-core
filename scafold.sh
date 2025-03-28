#!/bin/bash

# Script to read all example files in the ./examples directory
# and print their content for documentation purposes

# Colors for better readability
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if examples directory exists
if [ ! -d "./examples" ]; then
    echo -e "${YELLOW}Error: ./examples directory not found${NC}"
    exit 1
fi

# Get all files in the examples directory
files=(./examples/*)

# Check if there are any files
if [ ${#files[@]} -eq 0 ]; then
    echo -e "${YELLOW}No files found in ./examples directory${NC}"
    exit 0
fi

echo -e "${GREEN}Found ${#files[@]} files in examples directory${NC}\n"

# Loop through each file and print its content
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        
        echo -e "${BLUE}=================================${NC}"
        echo -e "${BLUE}File: $filename${NC}"
        echo -e "${BLUE}=================================${NC}"
        
        # Print file content with line numbers
        nl -ba "$file"
        
        echo -e "\n"
    fi
done

echo -e "${GREEN}All example files have been printed.${NC}"
echo -e "${GREEN}Please use this output to create documentation and README files.${NC}"