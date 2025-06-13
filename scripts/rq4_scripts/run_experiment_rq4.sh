#!/bin/bash

# Check if exactly one repository URL and one status number areprovided, and exit if not
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <testing-repo-url> <status-number>"
    exit 1
fi

# Assign the provided argument (repository URL) to a variable
repo_url_with_sha="$1"

# Split the input into link and sha
IFS=';' read -r TESTING_REPO_URL target_sha <<< "$repo_url_with_sha"

# Output the url
echo "Url: $TESTING_REPO_URL"
echo "Sha: $target_sha"

# Assign the provided argument (status number) to a variable
status_number="$2"

echo "🚀 Running experiment for: $TESTING_REPO_URL - $target_sha"
echo "Status number: $status_number"

# Combine URL and SHA with semicolon
url_with_sha="${TESTING_REPO_URL};${target_sha}"

if [ "$status_number" = "1" ]; then
    scripts=("run_pymop_25.sh" "run_dynapyt_25.sh" "run_dylin_25.sh" "run_dynapyt_libs.sh" "run_dylin_libs.sh")
else
    scripts=("run_pymop_28.sh" "run_dynapyt_28.sh" "run_dylin_28.sh")
fi

# Run the original script
echo "🚀 Running run_original.sh on $TESTING_REPO_URL with SHA $target_sha..."
if timeout 3600 bash "run_original.sh" "$url_with_sha"; then
    echo "✅ Finished run_original.sh on $TESTING_REPO_URL"

    # Run pymop and dynapyt scripts sequentially
    for script in "${scripts[@]}"; do
        echo "🚀 Running $script on $TESTING_REPO_URL with SHA $target_sha..."
        if timeout 3600 bash "$script" "$url_with_sha"; then
            echo "✅ Finished $script on $TESTING_REPO_URL"
        else
            echo "❌ $script failed for $TESTING_REPO_URL. Continuing to the next script..."
        fi
    done
else
    echo "❌ run_original.sh failed, skipping remaining scripts for $TESTING_REPO_URL"
fi

echo "✅ Experiment completed for $TESTING_REPO_URL with SHA $target_sha!"
echo "------------------------------------------"


echo "🎉 All experiments completed!"