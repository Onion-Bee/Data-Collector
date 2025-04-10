# kid_info_and_mchat.py

import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime
import json

# ---------- Phase 1: Collect Kid's Information ----------
def submit_info():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    gender = gender_entry.get().strip()

    if not name or not age or not gender:
        info_status_label.config(text="Please enter name, age, and gender.", foreground="red")
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

    info_status_label.config(text="Info saved! Starting M-CHAT-RF...", foreground="green")
    root.after(1000, lambda: [root.destroy(), show_initial()])  # Next: M-CHAT

# GUI for Kid Info
root = tk.Tk()
root.title("Enter Kid's Information")
root.geometry("300x250")
root.resizable(False, False)

ttk.Label(root, text="Kid's Name:").pack(pady=(20, 5))
name_entry = ttk.Entry(root, width=25)
name_entry.pack()

ttk.Label(root, text="Kid's Age:").pack(pady=(10, 5))
age_entry = ttk.Entry(root, width=25)
age_entry.pack()

ttk.Label(root, text="Kid's Gender:").pack(pady=(10, 5))
gender_entry = ttk.Entry(root, width=25)
gender_entry.pack()

submit_button = ttk.Button(root, text="Submit", command=submit_info)
submit_button.pack(pady=(20, 10))

info_status_label = ttk.Label(root, text="")
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

def submit_initial():
    red_flags = 0
    for i in range(len(initial_questions)):
        answer = initial_var_list[i].get()
        mchat_initial_answers[f"Q{i+1}"] = answer
        if answer == "No":
            red_flags += 1

    window_initial.destroy()

    if red_flags >= initial_threshold:
        show_followup()
    else:
        save_mchat_results(red_flags, None, "Pass", mchat_initial_answers, None)

def submit_followup():
    red_flags_followup = 0
    for i in range(len(followup_questions)):
        answer = followup_var_list[i].get()
        mchat_followup_answers[f"Followup_Q{i+1}"] = answer
        if answer == "No":
            red_flags_followup += 1

    window_followup.destroy()
    outcome = "High Risk" if red_flags_followup >= followup_threshold else "Moderate Risk"

    save_mchat_results(sum(1 for a in mchat_initial_answers.values() if a == "No"),
                       red_flags_followup, outcome, mchat_initial_answers, mchat_followup_answers)

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

def show_initial():
    global window_initial, initial_var_list
    window_initial = tk.Tk()
    window_initial.title("M-CHAT-RF Screening (Initial)")
    window_initial.geometry("500x600")

    canvas = tk.Canvas(window_initial, width=480, height=550)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(window_initial, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    ttk.Label(frame, text="Answer the following questions (Yes/No):", wraplength=460).pack(pady=10)
    initial_var_list = []
    for q in initial_questions:
        q_frame = ttk.Frame(frame)
        q_frame.pack(fill="x", padx=10, pady=3)
        ttk.Label(q_frame, text=q, wraplength=450).pack(anchor="w")
        var = tk.StringVar(value="Yes")
        initial_var_list.append(var)
        for option in ["Yes", "No"]:
            ttk.Radiobutton(q_frame, text=option, variable=var, value=option).pack(side="left", padx=5)

    ttk.Button(frame, text="Submit Answers", command=submit_initial).pack(pady=15)
    window_initial.mainloop()

def show_followup():
    global window_followup, followup_var_list
    window_followup = tk.Tk()
    window_followup.title("M-CHAT-RF Screening (Follow-Up)")
    window_followup.geometry("500x400")

    ttk.Label(window_followup, text="Follow-Up Questions (Yes/No):").pack(pady=10)
    followup_var_list = []
    for q in followup_questions:
        frame = ttk.Frame(window_followup)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text=q).pack(anchor="w")
        var = tk.StringVar(value="Yes")
        followup_var_list.append(var)
        for option in ["Yes", "No"]:
            ttk.Radiobutton(frame, text=option, variable=var, value=option).pack(side="left", padx=5)

    ttk.Button(window_followup, text="Submit Follow-Up Answers", command=submit_followup).pack(pady=15)
    window_followup.mainloop()

root.mainloop()
