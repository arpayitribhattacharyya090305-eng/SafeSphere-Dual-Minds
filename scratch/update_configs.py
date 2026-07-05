import glob
import re

files = glob.glob("frontend/pages/*.py")
files.append("frontend/app.py")

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if st.set_page_config is in the file
    if "st.set_page_config" in content:
        # Match set_page_config block
        # We look for st.set_page_config(args...)
        pattern = r"st\.set_page_config\(([^)]+)\)"
        match = re.search(pattern, content)
        if match:
            args = match.group(1)
            # If initial_sidebar_state is already set, update or keep it
            if "initial_sidebar_state" not in args:
                new_args = f"{args.strip()}, initial_sidebar_state=\"expanded\""
                # Standardize trailing commas
                new_args = re.sub(r",\s*,", ",", new_args)
                updated_content = content.replace(match.group(0), f"st.set_page_config({new_args})")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"Updated {file_path}")
            else:
                print(f"Already configured in {file_path}")
