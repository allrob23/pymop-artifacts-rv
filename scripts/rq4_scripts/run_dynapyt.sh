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

# Set the temporary directory to /tmp
TMPDIR=/tmp
echo "TMPDIR: $TMPDIR"

# Define the fixed repository URL for the DynaPyt project
DYNAPYT_REPO_URL="https://github.com/sola-st/DynaPyt.git"

# Extract the repository name from the URL
TESTING_REPO_NAME=$(basename -s .git "$TESTING_REPO_URL")

# Extract the developer ID from the URL
DEVELOPER_ID=$(echo "$TESTING_REPO_URL" | sed -E 's|https://github.com/([^/]+)/.*|\1|')

# Create combined name with developer ID and repo name
CLONE_DIR="${DEVELOPER_ID}-${TESTING_REPO_NAME}_DynaPyt"

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

# Create a virtual environment using Python's built-in venv
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Navigate to the testing project directory
cd "$TESTING_REPO_NAME" || { echo "Failed to enter directory $TESTING_REPO_NAME"; exit 1; }

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
pip install tensorflow

# Install memray and pytest-memray
pip install memray pytest-memray

# ------------------------------------------------------------------------------------------------
# Install DynaPyt
# ------------------------------------------------------------------------------------------------

# Return to the parent directory
cd ..

# Clone the DynaPyt repository into the current directory
git clone "$DYNAPYT_REPO_URL" || { echo "Failed to clone $DYNAPYT_REPO_URL"; exit 1; }

# Specify the source directory containing the Python DynaPyt files
SOURCE_DIR="$PWD/../Specs_libs/DynaPyt"

# Define the destination directory in the cloned DynaPyt repository
DESTINATION_DIR="$PWD/DynaPyt/src/dynapyt/analyses"

# Check if the source directory exists before attempting to copy files
if [ -d "$SOURCE_DIR" ]; then
    # Copy all Python files from the source directory to the destination
    cp "$SOURCE_DIR"/*.py "$DESTINATION_DIR"
else
    echo "Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

# Navigate into the cloned DynaPyt repository
cd DynaPyt

# Install the required dependencies for DynaPyt and the package itself
pip install -r requirements.txt
pip install .

# Navigate back to the root project directory
cd ..

# Generate a unique session ID for the DynaPyt run (in order to run multiple analyses in one run)
export DYNAPYT_SESSION_ID=$(uuidgen)
echo "DynaPyt Session ID: $DYNAPYT_SESSION_ID"

# Copy the analyses file to temp directory with session ID
cp "$PWD/../Specs_libs/dynapyt_analyses.txt" "$TMPDIR/dynapyt_analyses-$DYNAPYT_SESSION_ID.txt"

# Display contents of the copied file
cat "$TMPDIR/dynapyt_analyses-$DYNAPYT_SESSION_ID.txt"

# ------------------------------------------------------------------------------------------------
# Run the Instrumentation
# ------------------------------------------------------------------------------------------------

# Navigate to the testing project directory
cd "$TESTING_REPO_NAME"

# Record the start time of the instrumentation process
START_TIME=$(python3 -c 'import time; print(time.time())')

# Run DynaPyt instrumentation for analysis
python3 -m dynapyt.run_instrumentation --dir . --analysis dynapyt.analyses.Basic_Instrumentation.Basic_Instrumentation

# Record the end time and calculate the instrumentation duration
END_TIME=$(python3 -c 'import time; print(time.time())')
INSTRUMENTATION_TIME=$(python3 -c "print($END_TIME - $START_TIME)")

# ------------------------------------------------------------------------------------------------
# Run the tests
# ------------------------------------------------------------------------------------------------

# Record test start time
TEST_START_TIME=$(python3 -c 'import time; print(time.time())')

# Define the memory data directory name
MEMORY_DATA_DIR_NAME="memory-data-dynapyt"

# Run tests with 1-hour timeout and save output
timeout -k 9 3000 pytest --memray --trace-python-allocators --most-allocations=0 --memray-bin-path=./$MEMORY_DATA_DIR_NAME --continue-on-collection-errors > ${TESTING_REPO_NAME}_Output.txt
exit_code=$?

# Process test results if no timeout occurred
if [ $exit_code -ne 124 ] && [ $exit_code -ne 137 ]; then
    # Calculate test duration
    TEST_END_TIME=$(python3 -c 'import time; print(time.time())')
    TEST_TIME=$(python3 -c "print($TEST_END_TIME - $TEST_START_TIME)")

    # Show test summary
    tail -n 3 ${TESTING_REPO_NAME}_Output.txt
else
    echo "Timeout occurred"
    TEST_TIME="Timeout"
fi

# Return to parent directory
cd ..

# Clean up virtual environment
deactivate
rm -rf venv

# Ensure results directory exists
mkdir -p $CLONE_DIR

# Save test results
RESULTS_FILE="${CLONE_DIR}/${TESTING_REPO_NAME}_results.txt"
echo "Instrumentation Time: ${INSTRUMENTATION_TIME}s" >> $RESULTS_FILE
echo "Test Time: ${TEST_TIME}s" >> $RESULTS_FILE

# Copy all the txt files in the TESTING_REPO_NAME directory that end with _statistics.txt to the $CLONE_DIR directory
find "${TESTING_REPO_NAME}" -name "*_statistics.txt" -exec cp {} $CLONE_DIR/ \;

# Copy the ${TESTING_REPO_NAME}_Output.txt file to the $CLONE_DIR directory
cp "${TESTING_REPO_NAME}/${TESTING_REPO_NAME}_Output.txt" $CLONE_DIR/

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