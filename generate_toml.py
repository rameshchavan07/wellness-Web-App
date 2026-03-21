import json
import os

toml_content = []

# Process Firebase JSON
try:
    if os.path.exists("config/serviceAccountKey.json"):
        with open("config/serviceAccountKey.json", "r") as f:
            fb_data = json.load(f)
            toml_content.append("[firebase]")
            for k, v in fb_data.items():
                if isinstance(v, str):
                    if "\n" in v:
                        # Use standard quotes but properly escaped for TOML
                        # Or better: use triple quotes but Streamlit handles "\n" if we just literally write \n
                        v_escaped = v.replace("\n", "\\n").replace('"', '\\"')
                        toml_content.append(f'{k} = "{v_escaped}"')
                    else:
                        v_escaped = v.replace('"', '\\"')
                        toml_content.append(f'{k} = "{v_escaped}"')
                else:
                    toml_content.append(f'{k} = {json.dumps(v)}')
    toml_content.append("")
except Exception as e:
    print(f"Error reading serviceAccountKey: {e}")

# Process .env
try:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip(" \"'")
                    toml_content.append(f'{key} = "{val}"')
        toml_content.append("")
except Exception as e:
    print(f"Error reading .env: {e}")

toml_string = "\n".join(toml_content)
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/secrets.toml", "w") as f:
    f.write(toml_string)
print("Successfully created .streamlit/secrets.toml")
