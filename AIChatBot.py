import os
import tkinter as tk
from tkinter import ttk
import threading
import logging
from groq import Groq  

# Groq API Setup
os.environ["GROQ_API_KEY"] = "Enter groq key here"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Function to get the response from the Groq API
def get_response_from_groq(query):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": query,
        }
    ],
            model="llama-3.1-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Failed to get response from Groq API: {str(e)}")
        return f"Error: {str(e)}"

# Function to submit the query
def submit_query():
    response_text.delete(1.0, tk.END)
    progress_bar.start()  # Start the progress bar animation

    # Run the API call in a separate thread to avoid blocking the UI
    threading.Thread(target=fetch_response_thread, args=(query_entry.get("1.0", tk.END).strip(),)).start()

# Function to fetch the response and update the UI after fetching it
def fetch_response_thread(query):
    try:
        # Attempt to get a response from the API
        response = get_response_from_groq(query)
    except Exception as e:
        # If there's an error, set response to a meaningful error message
        response = f"An error occurred: {str(e)}"
    finally:
        # After receiving the response, update the text box and stop the progress bar
        response_text.insert(tk.END, response)
        progress_bar.stop()

# Function to handle Enter and Shift+Enter
def handle_keypress(event):
    if event.keysym == 'Return':
        if event.state & 0x0001:  # Shift key pressed
            query_entry.insert(tk.INSERT, '\n')
            query_entry.see(tk.END)  # Ensure the new line is visible
            current_height = int(query_entry.index('end-1c').split('.')[0])
            if current_height > 10:
                query_entry.configure(height=10)
            else:
                query_entry.configure(height=current_height)
        else:
            submit_query()
            return "break"
    current_height = int(query_entry.index('end-1c').split('.')[0])
    if current_height <= 10:
        query_entry.configure(height=current_height)

# Function to copy the AI response to the clipboard
def copy_response():
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(response_text.get("1.0", tk.END).strip())  # Append response to clipboard
    root.update()  # Update the UI to reflect the change

# Create a simple Tkinter window
root = tk.Tk()
root.title("AI Query")
root.configure(bg="#f0f0f0")

# Styling configurations
style = ttk.Style()
style.configure("TButton", padding=6, relief="raised", background="#4CAF50", foreground="black", font=("Helvetica", 12))
style.map("TButton",
          background=[('active', '#45a049')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

style.configure("TEntry", padding=5)
style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 12))

# Input field for the query
query_label = ttk.Label(root, text="Enter your query:")
query_label.pack(pady=(20, 5))

query_entry_frame = tk.Frame(root)
query_entry_frame.pack(pady=5, padx=20, fill='x')

query_entry = tk.Text(query_entry_frame, height=2, wrap='word', font=("Segoe UI", 10))
query_entry.pack(side='left', fill='both', expand=True)
query_entry.bind("<KeyPress>", handle_keypress)

# Submit button
submit_button = ttk.Button(root, text="Submit", command=submit_query)
submit_button.pack(pady=10)

# Progress bar for loading indication
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack(pady=10, fill='x', padx=20)

# Response text field
response_text = tk.Text(root, height=10, font=("Helvetica", 11), wrap='word')
response_text.pack(pady=10, expand=True, fill='both', padx= 20)

# Copy button to copy response to clipboard
copy_button = ttk.Button(root, text="Copy Response", command=copy_response)
copy_button.pack(pady=10)

root.mainloop()
