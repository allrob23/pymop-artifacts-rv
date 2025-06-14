#!/bin/bash

# Check if exactly one repository URL is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <testing-repo-url>"
    exit 1
fi

# Assign the provided repository URL with SHA to a variable
repo_url_with_sha="$1"

# Split the input into repository URL and SHA
IFS=';' read -r TESTING_REPO_URL target_sha <<< "$repo_url_with_sha"

# Output the URL and SHA
echo "Url: $TESTING_REPO_URL"
echo "Sha: $target_sha"

# Fixed repository URL for the mop-with-dynapt project
PYMOP_REPO_URL="https://github.com/allrob23/pymop-artifacts-rv.git"

# Extract the repository name from the URL
TESTING_REPO_NAME=$(basename -s .git "$TESTING_REPO_URL")

# Extract the developer ID from the URL
DEVELOPER_ID=$(echo "$TESTING_REPO_URL" | sed -E 's|https://github.com/([^/]+)/.*|\1|')

# Create combined name with developer ID and repo name
CLONE_DIR="${DEVELOPER_ID}-${TESTING_REPO_NAME}_PyMOP_curses"

# Create the directory if it does not exist
mkdir -p "$CLONE_DIR"

# Navigate to the project directory
cd "$CLONE_DIR" || { echo "Failed to enter directory $CLONE_DIR"; exit 1; }

# ------------------------------------------------------------------------------------------------
# Install the testing repository
# ------------------------------------------------------------------------------------------------

# Clone the testing repository and checkout specific SHA if provided
if [ -n "$target_sha" ]; then
    git clone "$TESTING_REPO_URL" && cd "$(basename "$TESTING_REPO_URL" .git)" && git checkout "$target_sha" && cd .. || { echo "Failed to clone/checkout $TESTING_REPO_URL at $target_sha"; exit 1; }
else
    git clone "$TESTING_REPO_URL" || { echo "Failed to clone $TESTING_REPO_URL"; exit 1; }
fi

# Navigate to the testing project directory
cd "$TESTING_REPO_NAME" || { echo "Failed to enter directory $TESTING_REPO_NAME"; exit 1; }

# Create a virtual environment in the project directory using Python's built-in venv
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from all requirement files if they exist
for file in *.txt; do
    if [ -f "$file" ]; then
        pip install -r "$file"
    fi
done

# Install the package with test dependencies using custom install script if available
if [ -f myInstall.sh ]; then
    bash ./myInstall.sh
else
    pip install .[dev,test,tests,testing]
fi

# Install required Python packages
pip install pytest
pip install numpy
pip install matplotlib
pip install pandas

# Install memray and pytest-memray
pip install memray pytest-memray

# ------------------------------------------------------------------------------------------------
# Install PyMOP
# ------------------------------------------------------------------------------------------------

# Return to the parent directory
cd ..

# Clone the pymop repository
git clone "$PYMOP_REPO_URL" || { echo "Failed to clone $PYMOP_REPO_URL"; exit 1; }

# Navigate to the pymop directory
cd pymop-artifacts-rv/pymop

# Install the project in editable mode with dev dependencies
pip install . || { echo "Failed to install mop-with-dynapt"; exit 1; }
pip install pytest-json-report

# ------------------------------------------------------------------------------------------------
# Run the tests
# ------------------------------------------------------------------------------------------------

# Navigate back to the root project directory
cd ../..

# Navigate into the testing repository
cd $TESTING_REPO_NAME

# Record the start time of the test execution
TEST_START_TIME=$(python3 -c 'import time; print(time.time())')

# Define the memory data directory name
MEMORY_DATA_DIR_NAME="memory-data-pymop"

# Run tests with 1-hour timeout and save output
timeout -k 9 3000 pytest --path="$PWD"/../pymop-artifacts-rv/pymop/specs-new --algo=D --memray --trace-python-allocators --most-allocations=0 --memray-bin-path=./$MEMORY_DATA_DIR_NAME --continue-on-collection-errors --json-report --json-report-indent=2 --statistics --statistics_file="D".json > ${TESTING_REPO_NAME}_Output.txt
exit_code=$?

# Process test results if no timeout occurred
if [ $exit_code -ne 124 ] && [ $exit_code -ne 137 ]; then
    # Record the end time and calculate the test execution duration
    TEST_END_TIME=$(python3 -c 'import time; print(time.time())')
    TEST_TIME=$(python3 -c "print($TEST_END_TIME - $TEST_START_TIME)")

    # Display the last few lines of the test output for quick status check
    tail -n 3 ${TESTING_REPO_NAME}_Output.txt
else
    echo "Timeout occurred"
    TEST_TIME="Timeout"
fi

# Clean up virtual environment
deactivate
rm -rf venv

# Return to parent directory
cd ..

# Ensure results directory exists
mkdir -p $CLONE_DIR

# Save test results
RESULTS_FILE="${CLONE_DIR}/${TESTING_REPO_NAME}_results.txt"
echo "Test Time: ${TEST_TIME}s" >> $RESULTS_FILE

# Copy the necessary files to the $CLONE_DIR directory
cp "${TESTING_REPO_NAME}/${TESTING_REPO_NAME}_Output.txt" $CLONE_DIR/
cp $TESTING_REPO_NAME/.report.json $CLONE_DIR/.report.json
cp $TESTING_REPO_NAME/D-full.json $CLONE_DIR/D-full.json
cp $TESTING_REPO_NAME/D-time.json $CLONE_DIR/D-time.json
cp $TESTING_REPO_NAME/D-violations.json $CLONE_DIR/D-violations.json

# Show all the files in the memory data directory
ls $TESTING_REPO_NAME/$MEMORY_DATA_DIR_NAME

# Copy the memory data to the results directory
cp -r $TESTING_REPO_NAME/$MEMORY_DATA_DIR_NAME $CLONE_DIR/

# Archive results
zip -r "${CLONE_DIR}.zip" $CLONE_DIR
mv "${CLONE_DIR}.zip" ..

# Return to main directory
cd ..

# Clean up project directory
rm -rf "$CLONE_DIR"
