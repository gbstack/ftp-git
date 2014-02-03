from PySide.QtCore import *
from PySide.QtGui import *
import sys
import git
import ftplib

class MainWindow(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		grid_layout = QGridLayout()
		self.setLayout(grid_layout)

		changed_files_table = QTableView()
		grid_layout.addWidget(changed_files_table, 0, 0, 5, 1)
		changed_files_model = QStandardItemModel()
		changed_files_table.setModel(changed_files_model)

		r = git.Repo('.')
		c = r.head.commit
		for f in c.stats.files.keys():
			print f
			changed_files_model.appendRow([QStandardItem(f)])

		# ftp part UI
		address_label = QLabel('Server Address')
		self.address_edit = QLineEdit()
		username_label = QLabel('Username')
		self.username_edit = QLineEdit()
		password_label = QLabel('Password')
		self.password_edit = QLineEdit()
		upload_btn = QPushButton('Upload')

		upload_btn.clicked.connect(self.uploadBtnClicked)

		grid_layout.addWidget(address_label, 0, 1, 1, 1)
		grid_layout.addWidget(self.address_edit, 0, 2, 1, 1)
		grid_layout.addWidget(username_label, 1, 1, 1, 1)
		grid_layout.addWidget(self.username_edit, 1, 2, 1, 1)
		grid_layout.addWidget(password_label, 2, 1, 1, 1)
		grid_layout.addWidget(self.password_edit, 2, 2, 1, 1)
		grid_layout.addWidget(upload_btn, 3, 1, 1, 1)

	def uploadBtnClicked(self):
		server_address = self.address_edit.text()
		username = self.username_edit.text()
		password = self.password_edit.text()

		ftp = ftplib.FTP(server_address)
		print ftp
		print ftp.login(username, password)

		print username, password

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()