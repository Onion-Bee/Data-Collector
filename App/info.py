# import sys
# import csv
# import json
# from datetime import datetime
# from PyQt5 import QtCore, QtGui, QtWidgets

# # ---------- Configuration Constants ----------
# BG_COLOR = "#F0F0F0"
# PRIMARY_COLOR = "#2C3E50"
# SECONDARY_COLOR = "#3498DB"
# FONT_NAME = "Segoe UI"
# SCQ_THRESHOLD = 15  # Total score threshold for further evaluation

# # ---------- Data Files ----------
# INFO_CSV = "kid_info.csv"
# RESULTS_CSV = "scq_results.csv"

# # ---------- SCQ Questions and Scoring ----------
# SCQ_QUESTIONS = [
#     "Is she/he now able to talk using short phrases or sentences?",
#     "Can you have a to-and-fro \"conversation\" with her/him that involves taking turns or building on what she/he has said?",
#     "Does she/he ever use gestures to indicate interest in something?",
#     "Does she/he ever point to express interest in something?",
#     "Does she/he ever bring objects over to show you something?",
#     "Does she/he look you in the eye when talking to you?",
#     "Does she/he ever seem overly sensitive to noise?",
#     "Does she/he respond when you call her/his name?",
#     "Does she/he smile back when someone smiles at her/him?",
#     "Does she/he ever show interest in other children her/his age?",
#     "Does she/he ever engage in \"pretend\" or \"make-believe\" play?",
#     "Does she/he ever use her/his index finger to point, to ask for something?",
#     "Does she/he ever use her/his index finger to point, to indicate interest in something?",
#     "Can she/he play appropriately with small toys (cars, dolls, building blocks) without just mouthing, fiddling, or dropping them?",
#     "Does she/he ever pretend objects are something else? (e.g., cup as a telephone)",
#     "Does she/he ever imitate you?",
#     "Does she/he ever imitate other children?",
#     "Does she/he respond positively when others approach her/him?",
#     "Does she/he try to comfort someone who is hurt or upset?",
#     "Does she/he enjoy being held or cuddled?",
#     "Does she/he get affected by unusual or unexpected noises?",
#     "Does she/he have any unusual preoccupations?",
#     "Does she/he have any compulsive or repetitive behaviors?",
#     "Does she/he ever injure herself deliberately (e.g., biting, banging head)?",
#     "Does she/he have any unusual sensory interests (e.g., sniffing objects)?",
#     "Does she/he display complex body movements (e.g., hand flapping)?",
#     "Does she/he ever repeat things that you or others have said (echolalia)?",
#     "Does she/he ever use stereotyped or repetitive speech?",
#     "Does she/he have difficulty with changes in routine or surroundings?",
#     "Does she/he have any special interests or hobbies?",
#     "Does she/he ever seem to be in a world of her/his own?",
#     "Does she/he ever become excessively distressed for no apparent reason?",
#     "Does she/he have difficulty understanding other people's feelings?",
#     "Does she/he ever laugh or giggle inappropriately?",
#     "Does she/he ever make unusual facial expressions?",
#     "Does she/he ever look at things from unusual angles?",
#     "Does she/he ever have any strange or unusual interests?",
#     "Has she/he ever seemed uninterested in interacting with you?",
#     "Does she/he tend to walk on her/his toes?",
#     "Does she/he have any unusual fears or anxieties?"
# ]

# # Autism-indicative response for each question ("Yes" or "No")
# SCQ_AUTISM_RESPONSE = [
#     "No", "No", "No", "No", "No", "No",
#     "Yes", "No", "No", "No",
#     "No", "No", "No", "No", "No",
#     "No", "No", "No", "No", "No",
#     "Yes", "Yes", "Yes", "Yes", "Yes",
#     "Yes", "Yes", "Yes", "Yes",
#     "Yes", "Yes", "Yes", "Yes", "Yes",
#     "Yes", "Yes", "Yes", "Yes",
#     "Yes", "Yes"
# ]

# # ---------- Helper Functions ----------
# def save_to_csv(file_path, data_dict):
#     write_header = False
#     try:
#         with open(file_path, 'r'):
#             pass
#     except FileNotFoundError:
#         write_header = True
#     with open(file_path, 'a', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=data_dict.keys())
#         if write_header:
#             writer.writeheader()
#         writer.writerow(data_dict)

# # ---------- Info Page ----------
# class InfoPage(QtWidgets.QWidget):
#     submitted = QtCore.pyqtSignal(dict)

#     def __init__(self):
#         super().__init__()
#         self.setLayout(QtWidgets.QVBoxLayout())
#         self.layout().setAlignment(QtCore.Qt.AlignTop)
#         self.layout().setSpacing(15)
#         self.setup_ui()

#     def setup_ui(self):
#         title = QtWidgets.QLabel("Child Information Entry")
#         title.setFont(QtGui.QFont(FONT_NAME, 18, QtGui.QFont.Bold))
#         title.setStyleSheet(f"color: {PRIMARY_COLOR}; margin-bottom: 10px;")
#         self.layout().addWidget(title, alignment=QtCore.Qt.AlignHCenter)

#         form_frame = QtWidgets.QFrame()
#         form_frame.setStyleSheet("QFrame { background: white; border-radius: 10px; padding: 20px; }")
#         form_layout = QtWidgets.QFormLayout(form_frame)
#         form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
#         form_layout.setHorizontalSpacing(20)
#         self.name_input = QtWidgets.QLineEdit()
#         self.age_input = QtWidgets.QLineEdit()
#         self.gender_input = QtWidgets.QLineEdit()
#         for widget in (self.name_input, self.age_input, self.gender_input):
#             widget.setFixedHeight(30)
#             widget.setStyleSheet("QLineEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; }")
#         form_layout.addRow("Full Name:", self.name_input)
#         form_layout.addRow("Age:", self.age_input)
#         form_layout.addRow("Gender:", self.gender_input)
#         self.layout().addWidget(form_frame)

#         self.status_label = QtWidgets.QLabel("")
#         self.layout().addWidget(self.status_label, alignment=QtCore.Qt.AlignHCenter)

#         submit_btn = QtWidgets.QPushButton("Submit Information")
#         submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#         submit_btn.setFixedHeight(40)
#         submit_btn.setStyleSheet(
#             f"QPushButton {{ background: {SECONDARY_COLOR}; color: white; border-radius: 5px; }}"
#             "QPushButton:hover { background: #5dade2; }"
#         )
#         submit_btn.clicked.connect(self.on_submit)
#         self.layout().addWidget(submit_btn)

#     def on_submit(self):
#         name = self.name_input.text().strip()
#         age = self.age_input.text().strip()
#         gender = self.gender_input.text().strip()
#         if not all((name, age, gender)):
#             self.status_label.setText("Please fill in all fields.")
#             self.status_label.setStyleSheet("color: red;")
#             return
#         info = {"name": name, "age": age, "gender": gender, "timestamp": datetime.now().isoformat()}
#         save_to_csv(INFO_CSV, info)
#         self.status_label.setText("Information saved. Proceeding...")
#         QtCore.QTimer.singleShot(800, lambda: self.submitted.emit(info))

# # ---------- SCQ Questionnaire Page ----------
# class QuestionnairePage(QtWidgets.QWidget):
#     finished = QtCore.pyqtSignal(int, dict, dict)

#     def __init__(self, questions, kid_info):
#         super().__init__()
#         self.questions = questions
#         self.kid_info = kid_info
#         self.vars = []
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.setAlignment(QtCore.Qt.AlignTop)
#         layout.setSpacing(10)
#         self.setup_ui(layout)

#     def setup_ui(self, layout):
#         title = QtWidgets.QLabel("Social Communication Questionnaire (SCQ)")
#         title.setFont(QtGui.QFont(FONT_NAME, 16, QtGui.QFont.Bold))
#         title.setStyleSheet(f"color: {PRIMARY_COLOR}; margin: 10px 0;")
#         layout.addWidget(title, alignment=QtCore.Qt.AlignHCenter)

#         info_lbl = QtWidgets.QLabel(f"Child: {self.kid_info['name']}, Age: {self.kid_info['age']}, Gender: {self.kid_info['gender']}")
#         info_lbl.setFont(QtGui.QFont(FONT_NAME, 11))
#         layout.addWidget(info_lbl, alignment=QtCore.Qt.AlignHCenter)

#         scroll = QtWidgets.QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("QScrollArea { border: none; }")
#         container = QtWidgets.QWidget(); container_layout = QtWidgets.QVBoxLayout(container)
#         container_layout.setSpacing(15)

#         for q in self.questions:
#             frame = QtWidgets.QFrame()
#             frame.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 15px; }")
#             v_layout = QtWidgets.QVBoxLayout(frame)
#             lbl = QtWidgets.QLabel(q)
#             lbl.setWordWrap(True)
#             lbl.setFont(QtGui.QFont(FONT_NAME, 11))
#             v_layout.addWidget(lbl)
#             btn_layout = QtWidgets.QHBoxLayout()
#             group = QtWidgets.QButtonGroup(frame)
#             yes = QtWidgets.QRadioButton("Yes"); no = QtWidgets.QRadioButton("No")
#             yes.setChecked(True)
#             for btn in (yes, no):
#                 btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#                 btn_layout.addWidget(btn)
#                 group.addButton(btn)
#             v_layout.addLayout(btn_layout)
#             container_layout.addWidget(frame)
#             self.vars.append(group)

#         scroll.setWidget(container)
#         layout.addWidget(scroll)

#         submit_btn = QtWidgets.QPushButton("Submit SCQ")
#         submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#         submit_btn.setFixedHeight(40)
#         submit_btn.setStyleSheet(
#             f"QPushButton {{ background: {SECONDARY_COLOR}; color: white; border-radius: 5px; }}"
#             "QPushButton:hover { background: #5dade2; }"
#         )
#         submit_btn.clicked.connect(self.on_submit)
#         layout.addWidget(submit_btn)

#     def on_submit(self):
#         answers = {f"Q{i+1}": ('Yes' if grp.checkedButton().text() == 'Yes' else 'No')
#                    for i, grp in enumerate(self.vars)}
#         score = sum(1 for i, resp in enumerate(answers.values())
#                     if resp == SCQ_AUTISM_RESPONSE[i])
#         self.finished.emit(score, answers, self.kid_info)

# # ---------- Main Application ----------
# class SCQApp(QtWidgets.QStackedWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("SCQ Screening Tool")
#         self.setFixedSize(700, 800)
#         self.setStyleSheet(f"QWidget {{ background: {BG_COLOR}; font-family: {FONT_NAME}; }}")
#         self.init_ui()

#     def init_ui(self):
#         self.info_page = InfoPage()
#         self.info_page.submitted.connect(self.start_questionnaire)
#         self.addWidget(self.info_page)

#     def start_questionnaire(self, kid_info):
#         self.question_page = QuestionnairePage(SCQ_QUESTIONS, kid_info)
#         self.question_page.finished.connect(self.handle_finish)
#         self.addWidget(self.question_page)
#         self.setCurrentWidget(self.question_page)

#     def handle_finish(self, score, answers, kid_info):
#         outcome = "Further evaluation recommended" if score >= SCQ_THRESHOLD else "Screening indicates low risk"
#         record = {
#             "timestamp": datetime.now().isoformat(),
#             "name": kid_info['name'],
#             "age": kid_info['age'],
#             "gender": kid_info['gender'],
#             "scq_score": score,
#             "outcome": outcome,
#             "answers": json.dumps(answers)
#         }
#         save_to_csv(RESULTS_CSV, record)
#         QtWidgets.QMessageBox.information(self, "SCQ Result", f"Score: {score}\nOutcome: {outcome}")
#         self.close()

# # ---------- Entry Point ----------
# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     app.setStyle("Fusion")
#     win = SCQApp()
#     win.show()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()
import sys
import os
import csv
import json
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets

# ---------- Configuration Constants ----------
BG_COLOR = "#F0F0F0"
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
FONT_NAME = "Segoe UI"
SCQ_THRESHOLD = 15  # Total score threshold for further evaluation
LOG_DIR = "logs"

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# ---------- Data Files ----------
INFO_CSV = os.path.join(LOG_DIR, "kid_info.csv")
RESULTS_CSV = os.path.join(LOG_DIR, "scq_results.csv")

# ---------- SCQ Questions and Scoring ----------
SCQ_QUESTIONS = [
    "Is she/he now able to talk using short phrases or sentences?",
    "Can you have a to-and-fro \"conversation\" with her/him that involves taking turns or building on what she/he has said?",
    "Does she/he ever use gestures to indicate interest in something?",
    "Does she/he ever point to express interest in something?",
    "Does she/he ever bring objects over to show you something?",
    "Does she/he look you in the eye when talking to you?",
    "Does she/he ever seem overly sensitive to noise?",
    "Does she/he respond when you call her/his name?",
    "Does she/he smile back when someone smiles at her/him?",
    "Does she/he ever show interest in other children her/his age?",
    "Does she/he ever engage in \"pretend\" or \"make-believe\" play?",
    "Does she/he ever use her/his index finger to point, to ask for something?",
    "Does she/he ever use her/his index finger to point, to indicate interest in something?",
    "Can she/he play appropriately with small toys (cars, dolls, building blocks) without just mouthing, fiddling, or dropping them?",
    "Does she/he ever pretend objects are something else? (e.g., cup as a telephone)",
    "Does she/he ever imitate you?",
    "Does she/he ever imitate other children?",
    "Does she/he respond positively when others approach her/him?",
    "Does she/he try to comfort someone who is hurt or upset?",
    "Does she/he enjoy being held or cuddled?",
    "Does she/he get affected by unusual or unexpected noises?",
    "Does she/he have any unusual preoccupations?",
    "Does she/he have any compulsive or repetitive behaviors?",
    "Does she/he ever injure herself deliberately (e.g., biting, banging head)?",
    "Does she/he have any unusual sensory interests (e.g., sniffing objects)?",
    "Does she/he display complex body movements (e.g., hand flapping)?",
    "Does she/he ever repeat things that you or others have said (echolalia)?",
    "Does she/he ever use stereotyped or repetitive speech?",
    "Does she/he have difficulty with changes in routine or surroundings?",
    "Does she/he have any special interests or hobbies?",
    "Does she/he ever seem to be in a world of her/his own?",
    "Does she/he ever become excessively distressed for no apparent reason?",
    "Does she/he have difficulty understanding other people's feelings?",
    "Does she/he ever laugh or giggle inappropriately?",
    "Does she/he ever make unusual facial expressions?",
    "Does she/he ever look at things from unusual angles?",
    "Does she/he ever have any strange or unusual interests?",
    "Has she/he ever seemed uninterested in interacting with you?",
    "Does she/he tend to walk on her/his toes?",
    "Does she/he have any unusual fears or anxieties?"
]

# Autism-indicative response for each question ("Yes" or "No")
SCQ_AUTISM_RESPONSE = [
    "No", "No", "No", "No", "No", "No",
    "Yes", "No", "No", "No",
    "No", "No", "No", "No", "No",
    "No", "No", "No", "No", "No",
    "Yes", "Yes", "Yes", "Yes", "Yes",
    "Yes", "Yes", "Yes", "Yes",
    "Yes", "Yes", "Yes", "Yes", "Yes",
    "Yes", "Yes", "Yes", "Yes",
    "Yes", "Yes"
]

# ---------- Helper Functions ----------
def save_to_csv(file_path, data_dict):
    """Append a row to CSV, creating header if file doesn't exist."""
    write_header = not os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(data_dict)

# ---------- Info Page ----------
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

# ---------- SCQ Questionnaire Page ----------
class QuestionnairePage(QtWidgets.QWidget):
    finished = QtCore.pyqtSignal(int, dict, dict)

    def __init__(self, questions, kid_info):
        super().__init__()
        self.questions = questions
        self.kid_info = kid_info
        self.vars = []
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(10)
        self.setup_ui(layout)

    def setup_ui(self, layout):
        title = QtWidgets.QLabel("Social Communication Questionnaire (SCQ)")
        title.setFont(QtGui.QFont(FONT_NAME, 16, QtGui.QFont.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR}; margin: 10px 0;")
        layout.addWidget(title, alignment=QtCore.Qt.AlignHCenter)

        info_lbl = QtWidgets.QLabel(f"Child: {self.kid_info['name']}, Age: {self.kid_info['age']}, Gender: {self.kid_info['gender']}")
        info_lbl.setFont(QtGui.QFont(FONT_NAME, 11))
        layout.addWidget(info_lbl, alignment=QtCore.Qt.AlignHCenter)

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

        submit_btn = QtWidgets.QPushButton("Submit SCQ")
        submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        submit_btn.setFixedHeight(40)
        submit_btn.setStyleSheet(
            f"QPushButton {{ background: {SECONDARY_COLOR}; color: white; border-radius: 5px; }}"
            "QPushButton:hover { background: #5dade2; }"
        )
        submit_btn.clicked.connect(self.on_submit)
        layout.addWidget(submit_btn)

    def on_submit(self):
        answers = {f"Q{i+1}": ('Yes' if grp.checkedButton().text() == 'Yes' else 'No')
                   for i, grp in enumerate(self.vars)}
        score = sum(1 for i, resp in enumerate(answers.values())
                    if resp == SCQ_AUTISM_RESPONSE[i])
        self.finished.emit(score, answers, self.kid_info)

# ---------- Main Application ----------
class SCQApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCQ Screening Tool")
        self.setFixedSize(700, 800)
        self.setStyleSheet(f"QWidget {{ background: {BG_COLOR}; font-family: {FONT_NAME}; }}")
        self.init_ui()

    def init_ui(self):
        self.info_page = InfoPage()
        self.info_page.submitted.connect(self.start_questionnaire)
        self.addWidget(self.info_page)

    def start_questionnaire(self, kid_info):
        self.question_page = QuestionnairePage(SCQ_QUESTIONS, kid_info)
        self.question_page.finished.connect(self.handle_finish)
        self.addWidget(self.question_page)
        self.setCurrentWidget(self.question_page)

    def handle_finish(self, score, answers, kid_info):
        outcome = "Further evaluation recommended" if score >= SCQ_THRESHOLD else "Screening indicates low risk"
        record = {
            "timestamp": datetime.now().isoformat(),
            "name": kid_info['name'],
            "age": kid_info['age'],
            "gender": kid_info['gender'],
            "scq_score": score,
            "outcome": outcome,
            "answers": json.dumps(answers)
        }
        save_to_csv(RESULTS_CSV, record)
        QtWidgets.QMessageBox.information(self, "SCQ Result", f"Score: {score}\nOutcome: {outcome}")
        self.close()

# ---------- Entry Point ----------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SCQApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
