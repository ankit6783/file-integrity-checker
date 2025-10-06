import os
import json
import hashlib

# --- Hashing Function (from Step 2) ---
BUFFER_SIZE = 65536

def get_file_hash(filepath):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha256_hash.update(data)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None
        
    return sha256_hash.hexdigest()

# --- Main Verification Logic ---
def verify_integrity(target_directory, baseline_file):
    """Verifies file integrity against a saved baseline."""
    # 1. Load the baseline
    try:
        with open(baseline_file, 'r') as f:
            baseline_hashes = json.load(f)
    except FileNotFoundError:
        print(f"Error: Baseline file '{baseline_file}' not found. Please create it first.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{baseline_file}'.")
        return

    print("Starting integrity check...")
    
    # 2. Initialize lists to store findings
    modified_files = []
    new_files = []
    
    # Create a copy of baseline files to find deleted ones
    checked_files = set()

    # 3. Walk the directory and check files
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(filepath, start=target_directory)
            
            checked_files.add(relative_path)

            current_hash = get_file_hash(filepath)
            
            if relative_path in baseline_hashes:
                # File exists in baseline, check if hash matches
                if baseline_hashes[relative_path] != current_hash:
                    modified_files.append(relative_path)
            else:
                # File is not in the baseline
                new_files.append(relative_path)

    # 4. Find deleted files
    # Any file in the baseline that was not checked must have been deleted
    deleted_files = set(baseline_hashes.keys()) - checked_files
    
    # 5. Report the results
    print("\n--- Integrity Check Report ---")
    if not modified_files and not new_files and not deleted_files:
        print("✅  All files are OK. No changes detected.")
    else:
        if modified_files:
            print("\n🚨 MODIFIED FILES:")
            for f in modified_files:
                print(f"  - {f}")
        
        if new_files:
            print("\n✨ NEW FILES DETECTED:")
            for f in new_files:
                print(f"  - {f}")
        
        if deleted_files:
            print("\n🗑️ DELETED FILES:")
            for f in deleted_files:
                print(f"  - {f}")
    print("----------------------------\n")


if __name__ == "__main__":
    MONITORED_DIRECTORY = "files_to_monitor"
    BASELINE_FILE = "baseline.json"
    
    if not os.path.isdir(MONITORED_DIRECTORY):
        print(f"Error: Directory '{MONITORED_DIRECTORY}' not found.")
    else:
        verify_integrity(MONITORED_DIRECTORY, BASELINE_FILE)