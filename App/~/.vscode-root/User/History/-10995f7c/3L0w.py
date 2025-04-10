# kid_info_and_mchat.py

import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime
import json

# Create a hidden root window.
root = tk.Tk()
root.withdraw()  # Hide the default root window.

style = ttk.Style()
style.theme_use("clam")

# ---------- Phase 1: Collect Kid's Information ----------
def submit_info():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    gender = gender_entry.get().strip()

    if not name or not age or not gender:
        info_status_label.config(text="Please complete all fields.", foreground="red")
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
    kid_info_win.after(1000, lambda: [kid_info_win.destroy(), show_initial()])  # Move to next phase

# Create Kid Info window as Toplevel
kid_info_win = tk.Toplevel(root)
kid_info_win.title("Kid Information")
kid_info_win.geometry("350x250")
kid_info_win.resizable(False, False)

main_frame = ttk.Frame(kid_info_win, padding="20 20 20 20")
main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

ttk.Label(main_frame, text="Enter Kid's Information", font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 15))
ttk.Label(main_frame, text="Name:").grid(column=0, row=1, sticky=tk.W, pady=5)
name_entry = ttk.Entry(main_frame, width=25)
name_entry.grid(column=1, row=1, pady=5)

ttk.Label(main_frame, text="Age:").grid(column=0, row=2, sticky=tk.W, pady=5)
age_entry = ttk.Entry(main_frame, width=25)
age_entry.grid(column=1, row=2, pady=5)

ttk.Label(main_frame, text="Gender:").grid(column=0, row=3, sticky=tk.W, pady=5)
gender_entry = ttk.Entry(main_frame, width=25)
gender_entry.grid(column=1, row=3, pady=5)

submit_button = ttk.Button(main_frame, text="Submit", command=submit_info)
submit_button.grid(column=0, row=4, columnspan=2, pady=15)

info_status_label = ttk.Label(main_frame, text="", font=("Arial", 10))
info_status_label.grid(column=0, row=5, columnspan=2)

# ---------- Phase 2: M-CHAT-RF Screening ----------

initial_questions = [
    "1. Does your child enjoy being read to?",
    "2. Does your child smile at you?",
    "3. Does your child respond when you call their name?",
    "4. Does your child point to objects to show interest?",
    "5. Does your child engage in pretend play?",
    "6. Does your child make eye contact?",
    "7. Does your child use gestures (e.g., waving)?",
    "8. Does your child imitate adult actions?",
    "9. Does your child enjoy social games?",
    "10. Does your child react typically to loud sounds?",
    "11. Does your child have a favorite toy?",
    "12. Does your child use their hands to communicate?",
    "13. Does your child show interest in other children?",
    "14. Does your child respond to facial expressions?",
    "15. Does your child share enjoyment with you?",
    "16. Does your child show varied facial expressions?",
    "17. Does your child use single words to communicate?",
    "18. Does your child understand simple instructions?",
    "19. Does your child engage in repetitive movements?",
    "20. Does your child show distress with changes in routine?"
]

followup_questions = [
    "Follow-Up 1: Difficulty understanding instructions?",
    "Follow-Up 2: Unusually withdrawn in social settings?",
    "Follow-Up 3: Repeats phrases or words repeatedly?"
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
    window_initial = tk.Toplevel(root)
    window_initial.title("M-CHAT-RF Screening (Initial)")
    window_initial.geometry("550x600")
    window_initial.resizable(False, False)

    canvas = tk.Canvas(window_initial, borderwidth=0, background="#f7f7f7", width=530, height=550)
    v_scrollbar = ttk.Scrollbar(window_initial, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    frame = ttk.Frame(canvas, padding="10 10 10 10")
    canvas.create_window((0, 0), window=frame, anchor="nw")

    ttk.Label(frame, text="Please answer the following questions:",
              font=("Arial", 14, "bold"), background="#f7f7f7")\
              .grid(column=0, row=0, columnspan=2, pady=(0, 15))
    initial_var_list = []
    for idx, question in enumerate(initial_questions):
        ttk.Label(frame, text=question, wraplength=500, font=("Arial", 10), background="#f7f7f7")\
            .grid(column=0, row=idx+1, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value="Yes")
        initial_var_list.append(var)
        options_frame = ttk.Frame(frame, background="#f7f7f7")
        options_frame.grid(column=1, row=idx+1, padx=5, pady=3, sticky="w")
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes")\
            .pack(side="left", padx=2)
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No")\
            .pack(side="left", padx=2)

    ttk.Button(frame, text="Submit Answers", command=submit_initial)\
        .grid(column=0, row=len(initial_questions)+2, columnspan=2, pady=20)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    window_initial.mainloop()

def show_followup():
    global window_followup, followup_var_list
    window_followup = tk.Toplevel(root)
    window_followup.title("M-CHAT-RF Screening (Follow-Up)")
    window_followup.geometry("550x400")
    window_followup.resizable(False, False)

    main_frame = ttk.Frame(window_followup, padding="20 20 20 20")
    main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    ttk.Label(main_frame, text="Follow-Up Questions:", font=("Arial", 14, "bold"))\
        .grid(column=0, row=0, columnspan=2, pady=(0,15))
    followup_var_list = []
    for idx, question in enumerate(followup_questions):
        ttk.Label(main_frame, text=question, wraplength=500, font=("Arial", 10))\
            .grid(column=0, row=idx+1, sticky="w", padx=5, pady=5)
        var = tk.StringVar(value="Yes")
        followup_var_list.append(var)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(column=1, row=idx+1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes")\
            .pack(side="left", padx=2)
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No")\
            .pack(side="left", padx=2)
    
    ttk.Button(main_frame, text="Submit Follow-Up Answers", command=submit_followup)\
        .grid(column=0, row=len(followup_questions)+1, columnspan=2, pady=20)
    window_followup.mainloop()

# Start the application by running the kid info window.
root.mainloop()
