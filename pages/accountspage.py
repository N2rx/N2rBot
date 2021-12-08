from theming.styles import globalStyles
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import return_data,write_data,get_account,Encryption
import sys,platform
def no_abort(a, b, c):
    sys.__excepthook__(a, b, c)
sys.excepthook = no_abort

class AccountsPage(QtWidgets.QWidget):

    def __init__(self,parent=None):
        super(AccountsPage, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, accountspage):
        self.accountspage = accountspage
        self.accountspage.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.accountspage.setGeometry(QtCore.QRect(60, 0, 1041, 601))
        self.accountspage.setStyleSheet("QComboBox::drop-down {    border: 0px;}QComboBox::down-arrow {    image: url(images/down_icon.png);    width: 14px;    height: 14px;}QComboBox{    padding: 1px 0px 1px 3px;}QLineEdit:focus {   border: none;   outline: none;}")
        font = QtGui.QFont()
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setFamily("Roboto")
        self.accounts_header = QtWidgets.QLabel(self.accountspage)
        self.accounts_header.setGeometry(QtCore.QRect(30, 10, 90, 31))
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setBold(False)
        font.setWeight(50)
        self.accounts_header.setFont(font)
        self.accounts_header.setStyleSheet("color: rgb(234, 239, 239);")
        self.accounts_header.setText("Accounts")
        self.tasks_card_3 = QtWidgets.QWidget(self.accountspage)
        self.tasks_card_3.setGeometry(QtCore.QRect(365, 70, 313, 501))
        self.tasks_card_3.setStyleSheet("background-color: {};border-radius: 20px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setBold(False)
        font.setWeight(50)
        self.save_btn = QtWidgets.QPushButton(self.tasks_card_3)
        self.save_btn.setGeometry(QtCore.QRect(70, 300, 86, 32))
        self.save_btn.setFont(font)
        self.save_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.save_btn.setStyleSheet("color: #FFFFFF;background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["primary"]))
        self.save_btn.setText("Save")  
        self.save_btn.clicked.connect(self.save_account)      
        self.account_header = QtWidgets.QLabel(self.tasks_card_3)
        self.account_header.setGeometry(QtCore.QRect(20, 15, 190, 36))
        font.setPointSize(18) if platform.system() == "Darwin" else font.setPointSize(18*.75)
        font.setBold(False)
        font.setWeight(50)
        self.account_header.setFont(font)
        self.account_header.setStyleSheet("color: rgb(212, 214, 214);border:  none;")
        self.account_header.setText("Accounts Manager")
        self.accountname_edit = QtWidgets.QLineEdit(self.tasks_card_3)
        self.accountname_edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.accountname_edit.setGeometry(QtCore.QRect(30, 60, 253, 21))
        font = QtGui.QFont()
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setFamily("Roboto")
        self.accountname_edit.setFont(font)
        self.accountname_edit.setStyleSheet("outline: 0;border: 1px solid {};border-width: 0 0 2px;color: rgb(234, 239, 239);".format(globalStyles["primary"]))
        self.accountname_edit.setPlaceholderText("account Name")
        self.accountemail_edit = QtWidgets.QLineEdit(self.tasks_card_3)
        self.accountemail_edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.accountemail_edit.setGeometry(QtCore.QRect(30, 120, 253, 21))
        font = QtGui.QFont()
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setFamily("Roboto")
        self.accountemail_edit.setFont(font)
        self.accountemail_edit.setStyleSheet("outline: 0;border: 1px solid {};border-width: 0 0 2px;color: rgb(234, 239, 239);".format(globalStyles["primary"]))
        self.accountemail_edit.setPlaceholderText("account Email")
        self.accountpass_edit = QtWidgets.QLineEdit(self.tasks_card_3)
        self.accountpass_edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.accountpass_edit.setGeometry(QtCore.QRect(30, 180, 253, 21))
        font = QtGui.QFont()
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setFamily("Roboto")
        self.accountpass_edit.setFont(font)
        self.accountpass_edit.setStyleSheet("outline: 0;border: 1px solid {};border-width: 0 0 2px;color: rgb(234, 239, 239);".format(globalStyles["primary"]))
        self.accountpass_edit.setPlaceholderText("account Pass")
        self.loadaccount_box = QtWidgets.QComboBox(self.tasks_card_3)
        self.loadaccount_box.setGeometry(QtCore.QRect(30, 350, 253, 26))
        self.loadaccount_box.setFont(font)
        self.loadaccount_box.setStyleSheet("outline: 0;border: 1px solid {};border-width: 0 0 2px;color: rgb(234, 239, 239);".format(globalStyles["primary"]))
        self.loadaccount_box.addItem("Load account")
        self.loadaccount_box.currentTextChanged.connect(self.load_account)
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setBold(False)
        font.setWeight(50)
        self.delete_btn = QtWidgets.QPushButton(self.tasks_card_3)
        self.delete_btn.setGeometry(QtCore.QRect(167, 300, 86, 32))
        self.delete_btn.setFont(font)
        self.delete_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.delete_btn.setStyleSheet("color: #FFFFFF;background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["primary"]))
        self.delete_btn.setText("Delete")
        self.delete_btn.clicked.connect(self.delete_account)
        self.set_data()
        QtCore.QMetaObject.connectSlotsByName(accountspage)

    
    def set_data(self):
        accounts = return_data("./data/accounts.json")
        for account in accounts:
            account_name = account["account_name"]
            self.loadaccount_box.addItem(account_name)
            self.parent().parent().createdialog.account_box.addItem(account_name)
   
    def load_account(self):
        account_name = self.loadaccount_box.currentText()
        p = get_account(account_name)
        if p is not None:
            self.accountname_edit.setText(p["account_name"])
            self.accountemail_edit.setText(p["account_email"])
            self.accountpass_edit.setText(p["account_pass"])
        return
    def save_account(self):
        account_name = self.accountname_edit.text()
        account_data={
            "account_name":account_name,
            "account_email": self.accountemail_edit.text(),
            "account_pass": (Encryption().encrypt(self.accountpass_edit.text())).decode("utf-8")
        }      
        accounts = return_data("./data/accounts.json")
        for p in accounts:
            if p["account_name"] == account_name:
                accounts.remove(p)
                break
        accounts.append(account_data)
        write_data("./data/accounts.json",accounts)
        if self.loadaccount_box.findText(account_name) == -1:
            self.loadaccount_box.addItem(account_name)
            self.parent().parent().createdialog.account_box.addItem(account_name)
        QtWidgets.QMessageBox.information(self, "N2r Bot", "Saved account")
    
    def delete_account(self):
        account_name = self.accountname_edit.text()
        accounts = return_data("./data/accounts.json")
        for account in accounts:
            if account["account_name"] == account_name:
                accounts.remove(account)
                break
        write_data("./data/accounts.json",accounts)
        self.loadaccount_box.removeItem(self.loadaccount_box.findText(account_name))
        self.parent().parent().createdialog.account_box.removeItem(self.parent().parent().createdialog.account_box.findText(account_name))

        self.loadaccount_box.setCurrentIndex(0)
        self.accountname_edit.setText("")
        self.accountname_edit.setText("")
        self.accountemail_edit.setText("")
        self.accountpass_edit.setText("")
        QtWidgets.QMessageBox.information(self, "N2r Bot", "Deleted account")
