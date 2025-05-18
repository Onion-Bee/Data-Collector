import sys
import csv
import json
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets

# ---------- Configuration Constants ----------
BG_COLOR = "#F0F0F0"
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
FONT_NAME = "Segoe UI"
INITIAL_THRESHOLD = 3
FOLLOWUP_THRESHOLD = 1

# ---------- Data Files ----------
INFO_CSV = "kid_info.csv"
RESULTS_CSV = "mchat_results.csv"

# ---------- Question Sets ----------
INITIAL_QUESTIONS = [
    "Does your child enjoy being read to?",
    "Does your child smile at you?",
    "Does your child respond when you call their name?",
    "Does your child point to objects to show interest?",
    "Does your child engage in pretend play?",
    "Does your child make eye contact?",
    "Does your child use gestures, such as waving?",
    "Does your child imitate adult actions?",
    "Does your child enjoy social games?",
    "Does your child react typically to loud sounds?",
    "Does your child have a favorite toy that they seek out?",
    "Does your child use their hands to communicate?",
    "Does your child show interest in other children?",
    "Does your child respond to facial expressions?",
    "Does your child try to share enjoyment with you?",
    "Does your child show varied facial expressions?",
    "Does your child use single words to communicate?",
    "Does your child understand simple instructions?",
    "Does your child engage in repetitive movements?",
    "Does your child show distress with changes in routine?",
]
FOLLOWUP_QUESTIONS = [
    "Does your child have difficulty understanding instructions?",
    "Does your child seem unusually withdrawn in social settings?",
    "Does your child repeat phrases or words over and over?",
]

# ---------- Helper Functions ----------
def save_to_csv(file_path, data_dict):
    write_header = False
    try:
        with open(file_path, 'r'):
            pass
    except FileNotFoundError:
        write_header = True
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(data_dict)

# ---------- Main Wizard Pages ----------
class InfoPage(QtWidgets.QWidget):
    submitted = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.layout().setSpacing(15)
        self.setup_ui()

    def setup_ui(self):
        title = QtWidgets.QLabel("Child Information Entry")
        title.setFont(QtGui.QFont(FONT_NAME, 18, QtGui.QFont.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR}; margin-bottom: 10px;")
        self.layout().addWidget(title, alignment=QtCore.Qt.AlignHCenter)

        form_frame = QtWidgets.QFrame()
        form_frame.setStyleSheet("QFrame { background: white; border-radius: 10px; padding: 20px; }")
        form_layout = QtWidgets.QFormLayout(form_frame)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setHorizontalSpacing(20)
        self.name_input = QtWidgets.QLineEdit()
        self.age_input = QtWidgets.QLineEdit()
        self.gender_input = QtWidgets.QLineEdit()
        for widget in (self.name_input, self.age_input, self.gender_input):
            widget.setFixedHeight(30)
            widget.setStyleSheet("QLineEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; }")
        form_layout.addRow("Full Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Gender:", self.gender_input)
        self.layout().addWidget(form_frame)

        self.status_label = QtWidgets.QLabel("")
        self.layout().addWidget(self.status_label, alignment=QtCore.Qt.AlignHCenter)

        submit_btn = QtWidgets.QPushButton("Submit Information")
        submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        submit_btn.setFixedHeight(40)
        submit_btn.setStyleSheet(
            f"QPushButton {{ background: {SECONDARY_COLOR}; color: white; border-radius: 5px; }}"
            "QPushButton:hover { background: #5dade2; }"
        )
        submit_btn.clicked.connect(self.on_submit)
        self.layout().addWidget(submit_btn)

    def on_submit(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_input.text().strip()
        if not all((name, age, gender)):
            self.status_label.setText("Please fill in all fields.")
            self.status_label.setStyleSheet("color: red;")
            return
        info = {"name": name, "age": age, "gender": gender, "timestamp": datetime.now().isoformat()}
        save_to_csv(INFO_CSV, info)
        self.status_label.setText("Information saved. Proceeding...")
        QtCore.QTimer.singleShot(800, lambda: self.submitted.emit(info))

class QuestionnairePage(QtWidgets.QWidget):
    finished_initial = QtCore.pyqtSignal(int, dict)
    finished_followup = QtCore.pyqtSignal(int, dict)

    def __init__(self, questions, is_followup=False):
        super().__init__()
        self.is_followup = is_followup
        self.questions = questions
        self.vars = []
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(10)
        self.setup_ui(layout)

    def setup_ui(self, layout):
        title_text = "Follow-Up Questions" if self.is_followup else "M-CHAT-R Screening"
        title = QtWidgets.QLabel(title_text)
        title.setFont(QtGui.QFont(FONT_NAME, 16, QtGui.QFont.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR}; margin: 10px 0;")
        layout.addWidget(title, alignment=QtCore.Qt.AlignHCenter)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        container = QtWidgets.QWidget(); container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setSpacing(15)

        for q in self.questions:
            frame = QtWidgets.QFrame()
            frame.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 15px; }")
            v_layout = QtWidgets.QVBoxLayout(frame)
            lbl = QtWidgets.QLabel(q)
            lbl.setWordWrap(True)
            lbl.setFont(QtGui.QFont(FONT_NAME, 11))
            v_layout.addWidget(lbl)
            btn_layout = QtWidgets.QHBoxLayout()
            group = QtWidgets.QButtonGroup(frame)
            yes = QtWidgets.QRadioButton("Yes"); no = QtWidgets.QRadioButton("No")
            yes.setChecked(True)
            for btn in (yes, no):
                btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                btn_layout.addWidget(btn)
                group.addButton(btn)
            v_layout.addLayout(btn_layout)
            container_layout.addWidget(frame)
            self.vars.append(group)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        submit_btn = QtWidgets.QPushButton("Submit Answers")
        submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        submit_btn.setFixedHeight(40)
        submit_btn.setStyleSheet(
            f"QPushButton {{ background: {SECONDARY_COLOR}; color: white; border-radius: 5px; }}"
            "QPushButton:hover { background: #5dade2; }"
        )
        submit_btn.clicked.connect(self.on_submit)
        layout.addWidget(submit_btn)

    def on_submit(self):
        answers = {f"Q{i+1}": ('No' if grp.checkedButton().text() == 'No' else 'Yes')
                   for i, grp in enumerate(self.vars)}
        red_flags = sum(1 for v in answers.values() if v == 'No')
        if self.is_followup:
            self.finished_followup.emit(red_flags, answers)
        else:
            self.finished_initial.emit(red_flags, answers)

class MChatApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("M-CHAT-R Screening Tool")
        self.setFixedSize(700, 800)
        self.setStyleSheet(f"QWidget {{ background: {BG_COLOR}; font-family: {FONT_NAME}; }}")
        self.init_ui()

    def init_ui(self):
        self.info_page = InfoPage()
        self.info_page.submitted.connect(self.start_initial)
        self.addWidget(self.info_page)

    def start_initial(self, kid_info):
        self.initial_page = QuestionnairePage(INITIAL_QUESTIONS)
        self.initial_page.finished_initial.connect(self.handle_initial)
        self.addWidget(self.initial_page)
        self.setCurrentWidget(self.initial_page)

    def handle_initial(self, red_flags, answers):
        if red_flags >= INITIAL_THRESHOLD:
            self.start_followup(red_flags, answers)
        else:
            self.save_results(red_flags, None, "Pass", answers, None)
            QtWidgets.QMessageBox.information(self, "Result", "Screening Passed.")
            self.close()

    def start_followup(self, init_flags, init_answers):
        self.followup_page = QuestionnairePage(FOLLOWUP_QUESTIONS, is_followup=True)
        self.followup_page.finished_followup.connect(
            lambda flags, ans: self.finish_followup(init_flags, init_answers, flags, ans)
        )
        self.addWidget(self.followup_page)
        self.setCurrentWidget(self.followup_page)

    def finish_followup(self, init_flags, init_answers, follow_flags, follow_answers):
        outcome = "High Risk" if follow_flags >= FOLLOWUP_THRESHOLD else "Moderate Risk"
        self.save_results(init_flags, follow_flags, outcome, init_answers, follow_answers)
        QtWidgets.QMessageBox.information(self, "Result", f"Outcome: {outcome}")
        self.close()

    def save_results(self, init_flags, follow_flags, outcome, init_ans, follow_ans):
        record = {
            "timestamp": datetime.now().isoformat(),
            "initial_red_flags": init_flags,
            "followup_red_flags": follow_flags or "",
            "outcome": outcome,
            "initial_answers": json.dumps(init_ans),
            "followup_answers": json.dumps(follow_ans) if follow_ans else ""
        }
        save_to_csv(RESULTS_CSV, record)

# ---------- Entry Point ----------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MChatApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
