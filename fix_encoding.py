"""Fix encoding issues"""

import os

files_to_fix = [
    "aerotest/core/ooda/ooda_engine.py",
    "aerotest/core/ooda/types.py",
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed: {file_path}")
    
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Converted from GBK: {file_path}")
        
        except Exception as e:
            print(f"Cannot fix: {file_path} - {str(e)}")
    
    except Exception as e:
        print(f"Error: {file_path} - {str(e)}")

print("\nEncoding fix completed")
