import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime
import json

# Configure style constants
BG_COLOR = "#F0F0F0"
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
FONT_NAME = "Segoe UI"

# ---------- Phase 1: Collect Kid's Information ----------
def submit_info():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    gender = gender_entry.get().strip()

    if not name or not age or not gender:
        info_status_label.config(text="Please fill in all fields.", foreground="red")
        return

    kid_info = {
        "name": name,
        "age": age,
        "gender": gender,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    info_csv = "kid_info.csv"
    try:
        with open(info_csv, 'x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=kid_info.keys())
            writer.writeheader()
            writer.writerow(kid_info)
    except FileExistsError:
        with open(info_csv, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=kid_info.keys())
            writer.writerow(kid_info)

    info_status_label.config(text="Information saved successfully!\nStarting M-CHAT-RF...", foreground=SECONDARY_COLOR)
    root.after(1000, lambda: [root.destroy(), show_initial()])

# Improved GUI for Kid Info
root = tk.Tk()
root.title("Child Information Entry")
root.geometry("400x300")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background=BG_COLOR, font=(FONT_NAME, 10))
style.configure("TButton", font=(FONT_NAME, 10), foreground="white", background=SECONDARY_COLOR)
style.configure("TEntry", fieldbackground="white")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="Child Information", font=(FONT_NAME, 16, "bold"), 
          foreground=PRIMARY_COLOR).pack(pady=(0, 20))

form_frame = ttk.Frame(main_frame)
form_frame.pack()

ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
name_entry = ttk.Entry(form_frame, width=25)
name_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
age_entry = ttk.Entry(form_frame, width=25)
age_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
gender_entry = ttk.Entry(form_frame, width=25)
gender_entry.grid(row=2, column=1, padx=5, pady=5)

submit_button = ttk.Button(main_frame, text="Submit Information", command=submit_info)
submit_button.pack(pady=20)

info_status_label = ttk.Label(main_frame, text="", wraplength=300, justify="center")
info_status_label.pack()

# ---------- Phase 2: M-CHAT-RF Screening ----------
initial_questions = [
    "1. Does your child enjoy being read to?",
    "2. Does your child smile at you?",
    "3. Does your child respond when you call their name?",
    "4. Does your child point to objects to show interest?",
    "5. Does your child engage in pretend play?",
    "6. Does your child make eye contact?",
    "7. Does your child use gestures, such as waving?",
    "8. Does your child imitate adult actions?",
    "9. Does your child enjoy social games?",
    "10. Does your child react typically to loud sounds?",
    "11. Does your child have a favorite toy that they seek out?",
    "12. Does your child use their hands to communicate?",
    "13. Does your child show interest in other children?",
    "14. Does your child respond to facial expressions?",
    "15. Does your child try to share enjoyment with you?",
    "16. Does your child show varied facial expressions?",
    "17. Does your child use single words to communicate?",
    "18. Does your child understand simple instructions?",
    "19. Does your child engage in repetitive movements?",
    "20. Does your child show distress with changes in routine?"
]

followup_questions = [
    "Follow-Up 1: Does your child have difficulty understanding instructions?",
    "Follow-Up 2: Does your child seem unusually withdrawn in social settings?",
    "Follow-Up 3: Does your child repeat phrases or words over and over?"
]

initial_threshold = 3
followup_threshold = 1

mchat_initial_answers = {}
mchat_followup_answers = {}

def save_mchat_results(initial_red_flags, followup_red_flags, outcome, initial_ans, followup_ans):
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial_red_flags": initial_red_flags,
        "followup_red_flags": followup_red_flags if followup_red_flags is not None else "",
        "outcome": outcome,
        "initial_answers": json.dumps(initial_ans),
        "followup_answers": json.dumps(followup_ans) if followup_ans is not None else ""
    }

    with open("mchat_results.csv", 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(result)

def submit_initial():
    red_flags = sum(1 for var in initial_var_list if var.get() == "No")
    mchat_initial_answers.update({f"Q{i+1}": var.get() for i, var in enumerate(initial_var_list)})
    
    window_initial.destroy()
    if red_flags >= initial_threshold:
        show_followup()
    else:
        save_mchat_results(red_flags, None, "Pass", mchat_initial_answers, None)

def submit_followup():
    red_flags_followup = sum(1 for var in followup_var_list if var.get() == "No")
    mchat_followup_answers.update({f"Followup_Q{i+1}": var.get() for i, var in enumerate(followup_var_list)})
    
    window_followup.destroy()
    outcome = "High Risk" if red_flags_followup >= followup_threshold else "Moderate Risk"
    save_mchat_results(sum(1 for a in mchat_initial_answers.values() if a == "No"),
                       red_flags_followup, outcome, mchat_initial_answers, mchat_followup_answers)

def create_questionnaire_window(title, questions, submit_callback):
    window = tk.Tk()
    window.title(title)
    window.geometry("600x700")
    window.configure(bg=BG_COLOR)
    
    container = ttk.Frame(window)
    container.pack(fill="both", expand=True, padx=20, pady=20)
    
    canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    ttk.Label(scrollable_frame, text="Please answer all questions:", 
             font=(FONT_NAME, 12, "bold"), foreground=PRIMARY_COLOR).pack(pady=10)
    
    var_list = []
    for i, question in enumerate(questions):
        frame = ttk.Frame(scrollable_frame, padding=10)
        frame.pack(fill="x", pady=4)
        
        ttk.Label(frame, text=question, wraplength=500, 
                 font=(FONT_NAME, 10)).pack(anchor="w")
        
        var = tk.StringVar(value="Yes")
        var_list.append(var)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Radiobutton(btn_frame, text="Yes", variable=var, 
                       value="Yes").pack(side="left", padx=10)
        ttk.Radiobutton(btn_frame, text="No", variable=var, 
                       value="No").pack(side="left", padx=10)
    
    ttk.Button(scrollable_frame, text="Submit Answers", 
              command=submit_callback).pack(pady=20)
    
    return window, var_list

def show_initial():
    global window_initial, initial_var_list, mchat_initial_answers
    window_initial, initial_var_list = create_questionnaire_window(
        "M-CHAT-R Screening - Initial", initial_questions, submit_initial
    )
    mchat_initial_answers = {}
    window_initial.mainloop()

def show_followup():
    global window_followup, followup_var_list, mchat_followup_answers
    window_followup, followup_var_list = create_questionnaire_window(
        "M-CHAT-R Screening - Follow Up", followup_questions, submit_followup
    )
    mchat_followup_answers = {}
    window_followup.mainloop()

root.mainloop()