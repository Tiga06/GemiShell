import os
import subprocess
import re
import requests
import json

# Replace with your actual API key
API_KEY = "API_KEY_HERE"

from datetime import datetime

def log_blocked_command(command, reason):
    with open("blocked_commands.log", "a") as log_file:
        log_file.write(f"[{datetime.now()}] BLOCKED: {command} | REASON: {reason}\n")

def analyze_rm_command(command):
    """Return severity level and explanation for the rm command."""
    if re.search(r"rm\s+-rf\s+/", command):
        return "CRITICAL", "⚠ This tries to recursively force delete the root directory. ABSOLUTELY NOT SAFE."
    elif re.search(r"rm\s+.*\*", command):
        return "RISKY", "⚠ This deletes multiple files at once using wildcard. Can be dangerous if misused."
    elif re.search(r'rm\s+"?\$?tmp_file"?', command):
        return "SAFE", "✅ This likely deletes a temporary file. Generally safe during scripting."
    else:
        return "UNKNOWN", "❓ Unrecognized 'rm' usage. Review carefully before proceeding."

def sanitize_command(command):
    """Sanitize command to avoid dangerous inputs with severity, explanation and user confirmation."""
    if "rm" in command:
        severity, explanation = analyze_rm_command(command)

        print(f"\n⚠  'rm' detected in the command!")
        print(f"🧾  Command: {command}")
        print(f"🔍  Severity: {severity}")
        print(f"📘  What it does: {explanation}")

        if severity == "CRITICAL":
            print("⛔ This command is too dangerous to run. Aborting.")
            log_blocked_command(command, explanation)
            raise ValueError("Critical 'rm' command blocked.")

        confirm = input("❓ Do you want to proceed with this command? (y/n): ")
        if confirm.lower() != 'y':
            log_blocked_command(command, f"User denied execution. Severity: {severity}")
            raise ValueError("Command aborted by user.")

        # All good, proceed
        return command

    # If 'rm' not in command, return as-is
    return command



def interpret_prompt(prompt):
    """Send prompt to Google API to interpret into Linux command."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Translate this request into a Linux shell command: {prompt}"}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        print("API Response:", response_data)  # Debug: Print the response
        try:
            # Extract command between ```bash and ``` tags
            full_text = response_data['candidates'][0]['content']['parts'][0]['text']
            command_match = re.search(r"```bash\n(.*?)\n```", full_text, re.DOTALL)
            if command_match:
                return command_match.group(1).strip()
            else:
                raise ValueError("No command found in response.")
        except KeyError:
            raise Exception("Unexpected response structure from API.")
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def execute_command(command):
    """Execute the shell command and return output."""
    try:
        sanitized_command = sanitize_command(command)
        result = subprocess.run(sanitized_command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except ValueError as e:
        return str(e)

def main():
    print("Welcome to the Linux Assistant! Type 'exit' to quit.")
    while True:
        user_input = input("Enter a Linux command request: ")
        if user_input.lower() == "exit":
            break
        try:
            command = interpret_prompt(user_input)
            print(f"Interpreted Command:\n{command}\n")

            # Check for script block
            if "#!/bin/bash" in command or "\n" in command:
                script_path = "generated_script.sh"
                with open(script_path, "w") as script_file:
                    script_file.write(command)
                os.chmod(script_path, 0o755)  # Make executable

                print(f"💾 Saved script to {script_path} and executing...\n")
                output = execute_command(f"./{script_path}")
            else:
                output = execute_command(command)

            print(f"📤 Output:\n{output}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
