import os

def check_file_for_null_bytes(file_path):
    """Check if a file contains null bytes and return their positions."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            has_null = b'\x00' in data
            positions = [i for i, b in enumerate(data) if b == 0]
            return has_null, positions
    except Exception as e:
        return f"Error reading file: {e}", []

def scan_directory(directory):
    """Scan a directory for Python files with null bytes."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                has_null, positions = check_file_for_null_bytes(file_path)
                
                if isinstance(has_null, str):  # Error occurred
                    print(f"{file_path}: {has_null}")
                elif has_null:
                    print(f"{file_path}: Contains {len(positions)} null bytes at positions {positions[:5]}{'...' if len(positions) > 5 else ''}")
                    
                    # Create a new file without null bytes
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        # Remove null bytes
                        clean_content = content.replace(b'\x00', b'')
                        
                        # Write back to a new file
                        new_file_path = file_path + '.clean'
                        with open(new_file_path, 'wb') as f:
                            f.write(clean_content)
                        
                        print(f"   - Created clean version at {new_file_path}")
                    except Exception as e:
                        print(f"   - Error creating clean file: {e}")

if __name__ == "__main__":
    print("Scanning app directory for null bytes in Python files...")
    scan_directory("app")
    print("Scan complete.") 