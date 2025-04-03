import tkinter as tk
from tkinter import filedialog, messagebox
import re

# Initial list of questions
questions = [
    {
        "id": 1,
        "text": (
            "A company employs a team of customer service agents to provide telephone and email support to customers. "
            "The company develops a webchat bot to provide automated answers to common customer queries. "
            "Which business benefit should the company expect as a result of creating the webchat bot solution?"
        ),
        "options": [
            "A. increased sales",
            "B. a reduced workload for the customer service agents",
            "C. improved product reliability"
        ],
        "answer": "B"
    },
    {
        "id": 2,
        "text": (
            "For a machine learning progress, how should you split data for training and evaluation?"
        ),
        "options": [
            "A. Use features for training and labels for evaluation.",
            "B. Randomly split the data into rows for training and rows for evaluation.",
            "C. Use labels for training and features for evaluation.",
            "D. Randomly split the data into columns for training and columns for evaluation."
        ],
        "answer": "B"
    },
    {
        "id": 4,
        "text": (
            "You build a machine learning model by using the automated machine learning user interface (UI). "
            "You need to ensure that the model meets the Microsoft transparency principle for responsible AI. "
            "What should you do?"
        ),
        "options": [
            "A. Set Validation type to Auto.",
            "B. Enable Explain best model.",
            "C. Set Primary metric to accuracy.",
            "D. Set Max concurrent iterations to 0."
        ],
        "answer": "B"
    },
    {
        "id": 8,
        "text": (
            "You are designing an AI system that empowers everyone, including people who have hearing, visual, and other impairments. "
            "This is an example of which Microsoft guiding principle for responsible AI?"
        ),
        "options": [
            "A. fairness",
            "B. inclusiveness",
            "C. reliability and safety",
            "D. accountability"
        ],
        "answer": "B"
    }
]


def parse_questions_from_content(content):
    """
    Parses questions from the provided file content. Only blocks that contain:
      - A line starting with "QUESTION NO:" followed immediately by a number.
      - A line starting with "Answer:"
    are accepted.
    The function builds a list of dictionaries with keys: "id", "text", "options", "answer".
    """
    parsed = []
    # Split content with "QUESTION NO:" as a delimiter (note: use re.MULTILINE for safe splitting)
    blocks = re.split(r"(?m)^QUESTION NO:\s*", content)
    for block in blocks:
        if not block.strip():
            continue  # Skip empty blocks

        lines = block.strip().splitlines()
        # The first line should contain the question id (and optionally part of the question text)
        first_line = lines[0].strip()
        match_id = re.match(r"(\d+)", first_line)
        if not match_id:
            continue  # Skip if no valid question id is found
        qid = int(match_id.group(1))
        # The remaining text on the first line (if any) is part of the question text.
        question_text = first_line[match_id.end():].strip()
        options = []
        answer = None

        state = "question_text"  # We use a state to know whether we are reading the question or its options.
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            # Look for the Answer line
            if line.startswith("Answer:"):
                answer = line.split("Answer:", 1)[1].strip()
                break
            # Check if the line is an option (it typically starts with a capital letter + ". ")
            if re.match(r"^[A-Z]\.\s", line):
                state = "options"
                options.append(line)
            else:
                if state == "question_text":
                    question_text += " " + line
                elif state == "options" and options:
                    # For multi-line options, append additional text to the last option
                    options[-1] += " " + line
        # Only add the question if both question text and answer were identified.
        if question_text and answer:
            parsed.append({
                "id": qid,
                "text": question_text,
                "options": options,
                "answer": answer
            })
    return parsed


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Q&A Bot")
        self.current_question = 0

        self.question_label = tk.Label(root, text="", wraplength=400, justify="left")
        self.question_label.pack(pady=10)

        self.var = tk.StringVar()
        self.options = []
        # Create 4 radio buttons (if a question has fewer options, extra ones will be hidden)
        for _ in range(4):
            rb = tk.Radiobutton(root, text="", variable=self.var, value="")
            rb.pack(anchor="w")
            self.options.append(rb)

        self.submit_button = tk.Button(root, text="Submit", command=self.check_answer)
        self.submit_button.pack(pady=5)

        self.next_button = tk.Button(root, text="Next", command=self.next_question)
        self.next_button.pack(pady=5)

        # Add a button to allow loading questions from a file
        self.load_button = tk.Button(root, text="Load Questions from File", command=self.load_from_file)
        self.load_button.pack(pady=5)

        self.load_question()

    def load_question(self):
        if self.current_question >= len(questions):
            messagebox.showinfo("End", "You've completed all questions!")
            self.root.quit()
            return

        question = questions[self.current_question]
        self.question_label.config(text=f"QUESTION NO: {question['id']}\n{question['text']}")
        self.var.set("")

        # Update radio buttons with question options or hide unused buttons
        for i, option in enumerate(question["options"]):
            self.options[i].config(text=option, value=option[0])
            self.options[i].pack(anchor="w")
        for i in range(len(question["options"]), len(self.options)):
            self.options[i].pack_forget()

    def check_answer(self):
        selected_answer = self.var.get()
        correct_answer = questions[self.current_question]["answer"]

        if selected_answer == correct_answer:
            messagebox.showinfo("Result", "✅ Correct!")
        else:
            messagebox.showerror("Result", f"❌ Incorrect! The correct answer is: {correct_answer}")

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(questions):
            self.load_question()
        else:
            messagebox.showinfo("End", "You've completed all questions!")
            self.root.quit()

    def load_from_file(self):
        """Opens a file dialog to load additional questions from a text file."""
        file_path = filedialog.askopenfilename(
            title="Select question file",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if not file_path:
            return  # User cancelled the file dialog.
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_questions = parse_questions_from_content(content)
            if new_questions:
                # Append new questions to the existing list
                questions.extend(new_questions)
                messagebox.showinfo("Load Successful", f"Added {len(new_questions)} questions from file.")
            else:
                messagebox.showinfo("No Valid Questions", "No valid questions were found in the file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
