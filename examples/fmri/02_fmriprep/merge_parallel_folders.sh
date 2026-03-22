#!/bin/bash

# Define your source directory (where the individual C337, C338, etc. folders live)
# and your new unified target directory.
SOURCE_DIR="$1"
TARGET_DIR="$2"

# Create the target directory if it doesn't already exist
mkdir -p "$TARGET_DIR"

# Loop through all directories in the source path
for SUBJ_DIR in "$SOURCE_DIR"/*/; do

    # Get just the folder name
    SUBJ_NAME=$(basename "$SUBJ_DIR")

    # Prevent the script from trying to sync the target directory into itself
    if [ "$SUBJ_NAME" == "$(basename "$TARGET_DIR")" ]; then
	continue
    fi

    echo "Merging $SUBJ_NAME into target directory..."
    
    # Sync contents.
    # -a ensures permissions and nested structures are preserved.
    # The trailing slash on "$SUBJ_DIR/" is critical: it tells rsync to move the
    # *contents* of the subject folder, not the folder itself.
    rsync -a "$SUBJ_DIR/" "$TARGET_DIR/"

done

echo "Merge complete. Please verify the contents of $TARGET_DIR."
