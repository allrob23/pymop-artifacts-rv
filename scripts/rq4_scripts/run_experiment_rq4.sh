#!/bin/bash

# Ensure the script stops on the first error
set -e

# Check if projects_evaluated.csv exists
if [ ! -f "projects_evaluated.csv" ]; then
    echo "❌ Error: projects_evaluated.csv not found!"
    exit 1
fi

# Count total projects (minus header)
total_projects=$(( $(wc -l < projects_evaluated.csv) - 1 ))
current_index=0

# Read the first line but don't process it
read -r first_line < projects_evaluated.csv 
echo "Skipping first line: $first_line"

scripts=("run_pymop.sh" "run_dynapyt.sh" "run_dylin.sh" "run_dynapyt_libs.sh")

# Process the remaining lines
sed 1d projects_evaluated.csv | while IFS=, read -r project repo_url target_sha; do
    # Keep only valid hexadecimal characters (0-9, a-f, A-F)
    target_sha=$(echo "$target_sha" | tr -cd '0-9a-fA-F')
    
    current_index=$((current_index + 1))
    echo "🚀 [$current_index/$total_projects] Running experiment for: $repo_url - $target_sha"

    # Combine URL and SHA with semicolon
    url_with_sha="${repo_url};${target_sha}"

    # Run the original script
    echo "🚀 Running run_original.sh on $repo_url with SHA $target_sha..."
    if timeout 3600 bash "run_original.sh" "$url_with_sha"; then
        echo "✅ Finished run_original.sh on $repo_url"

        # Run pymop and dynapyt scripts sequentially
        for script in "${scripts[@]}"; do
            echo "🚀 Running $script on $repo_url with SHA $target_sha..."
            if timeout 3600 bash "$script" "$url_with_sha"; then
                echo "✅ Finished $script on $repo_url"
            else
                echo "❌ $script failed for $repo_url. Continuing to the next script..."
            fi
        done
    else
        echo "❌ run_original.sh failed, skipping remaining scripts for $repo_url"
    fi

    echo "✅ Experiment completed for $repo_url with SHA $target_sha!"
    echo "------------------------------------------"

done

echo "🎉 All experiments completed!"