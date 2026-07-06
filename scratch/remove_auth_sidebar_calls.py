import glob
import os

pages_dir = "frontend/pages"
files = glob.glob(os.path.join(pages_dir, "*.py"))

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace render_auth_sidebar() call with empty space or comment
    if "render_auth_sidebar()" in content:
        # Replace the active execution call
        new_content = content.replace("render_auth_sidebar()", "# render_auth_sidebar()  # Handled globally in app.py")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Disabled duplicate render_auth_sidebar in {filepath}")
    else:
        print(f"No render_auth_sidebar call found in {filepath}")
