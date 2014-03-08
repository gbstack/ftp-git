from PySide.QtCore import *
from PySide.QtGui import *
import sys
import git
import ftplib
import sqlite3

class MainWindow(QWidget):
	def initDB(self):
		self.db_conn = sqlite3.connect('settings.db')
		cur = self.db_conn.cursor()
		try:
			cur.execute('create table ftp_servers(id integer primary key autoincrement, address varchar(255), username varchar(255), password varchar(255));')
		except sqlite3.OperationalError:
			print 'table already exists'

	def __init__(self):
		QWidget.__init__(self)

		self.initDB()

		grid_layout = QGridLayout()
		self.setLayout(grid_layout)

		changed_files_table = QTableView()
		grid_layout.addWidget(changed_files_table, 0, 0, 5, 1)
		changed_files_model = QStandardItemModel()
		changed_files_table.setModel(changed_files_model)

		r = git.Repo('.')
		c = r.head.commit
		self.changed_files = c.stats.files.keys()
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

		self.console_box = QTextEdit()
		self.console_box.setFixedHeight(100)
		grid_layout.addWidget(self.console_box, 6, 0, 1, 3)

		grid_layout.addWidget(address_label, 0, 1, 1, 1)
		grid_layout.addWidget(self.address_edit, 0, 2, 1, 1)
		grid_layout.addWidget(username_label, 1, 1, 1, 1)
		grid_layout.addWidget(self.username_edit, 1, 2, 1, 1)
		grid_layout.addWidget(password_label, 2, 1, 1, 1)
		grid_layout.addWidget(self.password_edit, 2, 2, 1, 1)
		grid_layout.addWidget(upload_btn, 3, 1, 1, 1)

		ftp_credentials = self.getFtpCredentials()
		if ftp_credentials:
			self.address_edit.setText(ftp_credentials[1])
			self.username_edit.setText(ftp_credentials[2])
			self.password_edit.setText(ftp_credentials[3])

	def printTextToConsole(self, text):
		print text
		original_text = self.console_box.toPlainText()
		self.console_box.setText(original_text+text+'\n')

	def getFtpCredentials(self):
		cur = self.db_conn.cursor()
		cur.execute('select * from ftp_servers')
		server = cur.fetchone()
		if server:
			return server
		else:
			return None

	def updateFtpCredentials(self, server_address, username, password):
		cur = self.db_conn.cursor()
		cur.execute('select * from ftp_servers where address="{0}"'.format(server_address))
		rows = cur.fetchall()
		if len(rows)>0:
			sql = 'update ftp_servers set address="{0}", username="{1}", password="{2}" where address="{0}"'.format(server_address, username, password)
			cur.execute(sql)
		else:
			sql = 'insert into ftp_servers(address, username, password) values("{0}", "{1}", "{2}")'.format(server_address, username, password)
			cur.execute(sql)
		self.db_conn.commit()

	def uploadBtnClicked(self):
		server_address = self.address_edit.text()
		username = self.username_edit.text()
		password = self.password_edit.text()
		self.updateFtpCredentials(server_address, username, password)

		ftp = ftplib.FTP()
		try:
			print ftp.connect(server_address)
		except Exception, e:
			print e
			self.printTextToConsole('Cannot connect to host')
			return

		try:
			login_status = ftp.login(username, password)
			self.printTextToConsole(login_status)
		except Exception, e:
			print e
			self.printTextToConsole('login failed')

		for filename in self.changed_files:
			f = open(filename)
			print ftp.storlines('STOR '+filename, f)
			f.close()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()