import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import re

def strip_terminal_codes(text):
    # Remove terminal control codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_installed_models():
    try:
        # Use the 'ollama list' command to list installed models
        command = ["ollama", "list"]
        result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
        result = strip_terminal_codes(result)  # Strip terminal control codes
        print("Command output:\n", result)  # Debugging statement

        # Split the output into lines
        lines = result.strip().split('\n')
        if len(lines) <= 1:
            print("No models found.")
            return []

        # Extract the model names from the lines that contain model information
        models = []
        for line in lines[1:]:  # Skip the header line
            parts = line.split()
            if len(parts) >= 4:  # Ensure the line has enough parts to be a valid model line
                models.append(parts[0])

        return models
    except subprocess.CalledProcessError as e:
        print("Error fetching models:", e.output)  # Debugging statement
        return []
    except FileNotFoundError:
        print("Error: 'ollama' command not found. Please ensure it is installed and in your PATH.")
        return []
    except Exception as e:
        print("An unexpected error occurred:", str(e))
        return []

def send_request():
    query = entry.get().strip()  # Get and trim the text from the input field
    model = model_var.get()  # Get the selected model from the combobox
    if not query:
        output_text.config(state=tk.NORMAL)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Error: Input field cannot be empty.")
        output_text.config(state=tk.DISABLED)
        return

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Loading...")
    output_text.config(state=tk.DISABLED)
    entry.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)
    clear_button.config(state=tk.DISABLED)

    def run_command():
        try:
            # Use the selected model in the command
            command = ["ollama", "run", model, query]
            # Execute the command and capture the output
            result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
            result = strip_terminal_codes(result)  # Strip terminal control codes
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)  # Display the result in the output text widget
            output_text.config(state=tk.DISABLED)
        except subprocess.CalledProcessError as e:
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "Error: " + strip_terminal_codes(e.output))
            output_text.config(state=tk.DISABLED)
        except FileNotFoundError:
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "Error: 'ollama' command not found. Please ensure it is installed and in your PATH.")
            output_text.config(state=tk.DISABLED)
        except Exception as e:
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "An error occurred: " + str(e))
            output_text.config(state=tk.DISABLED)
        finally:
            entry.config(state=tk.NORMAL)
            send_button.config(state=tk.NORMAL)
            clear_button.config(state=tk.NORMAL)

    threading.Thread(target=run_command).start()

def clear_fields():
    entry.delete(0, tk.END)
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)

# Setting up the main application window
app = tk.Tk()
app.title("Pulse")
app.geometry("600x400")  # Set a fixed size for the window

# Create a frame to hold the widgets
frame = tk.Frame(app, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

# Model selection
model_label = tk.Label(frame, text="Select Model:", font=("Helvetica", 14))
model_label.pack(pady=5)

model_var = tk.StringVar()
model_combobox = ttk.Combobox(frame, textvariable=model_var, font=("Helvetica", 14))
models = get_installed_models()
print("Installed models:", models)  # Debugging statement
model_combobox['values'] = models
if models:
    model_combobox.current(0)  # Set the default model
model_combobox.pack(pady=5)

# Input field
entry = tk.Entry(frame, width=50, font=("Helvetica", 14))
entry.pack(pady=10)  # Add some vertical padding

# Button frame
button_frame = tk.Frame(frame)
button_frame.pack(pady=10)

# Send button
send_button = tk.Button(button_frame, text="Send", command=send_request, font=("Helvetica", 14))
send_button.pack(side=tk.LEFT, padx=5)

# Clear button
clear_button = tk.Button(button_frame, text="Clear", command=clear_fields, font=("Helvetica", 14))
clear_button.pack(side=tk.LEFT, padx=5)

# Output text widget
output_text = tk.Text(frame, wrap=tk.WORD, font=("Helvetica", 14), bg="white", fg="black", height=10)
output_text.pack(pady=10, fill=tk.BOTH, expand=True)  # Add some vertical padding
output_text.config(state=tk.DISABLED)  # Make the output text widget read-only

# Run the application
app.mainloop()