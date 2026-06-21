#!/bin/bash

output_file="prompts.json"

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required for safe JSON generation. Install it first." >&2
    exit 1
fi

# Enable nullglob so the array is empty if no files match
shopt -s nullglob
files=(text/*.txt)

if [ ${#files[@]} -eq 0 ]; then
    echo "No .txt files found in the text/ directory." >&2
    exit 0
fi

# Loop through files, create an individual JSON object for each, 
# and then use jq -s 'add' to merge the stream of objects into one.
for file in "${files[@]}"; do
    filename=$(basename "$file")
    # --rawfile reads the entire file content exactly as-is into a variable
    jq -n --arg k "$filename" --rawfile v "$file" '{($k): $v}'
done | jq -s 'add' > "$output_file"

echo "Dumped ${#files[@]} files into $output_file"