import glob
import os
import re

pages_dir = "frontend/pages"
files = glob.glob(os.path.join(pages_dir, "*.py"))

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Match st.set_page_config(...) spanning one or more lines
    pattern = r"st\.set_page_config\([^)]+\)"
    match = re.search(pattern, content)
    if match:
        original = match.group(0)
        
        start_idx = match.start()
        lookback = content[max(0, start_idx-30):start_idx]
        if "try:" in lookback:
            print(f"Already wrapped in {filepath}")
            continue
            
        wrapped = f"try:\n    {original}\nexcept Exception:\n    pass"
        new_content = content.replace(original, wrapped)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Wrapped st.set_page_config in {filepath}")
    else:
        print(f"No st.set_page_config found in {filepath}")
