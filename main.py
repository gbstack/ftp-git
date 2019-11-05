#coding: utf-8

from PySide2.QtCore import *
from PySide2.QtGui import *
import sys
import git
import ftplib
import sqlite3
import os
import inspect
import webbrowser
import urllib.request, urllib.error, urllib.parse

from PySide2.QtWidgets import QVBoxLayout, QWidget, QCommandLinkButton, QLabel, QMessageBox, QGridLayout, QTableView, \
	QLineEdit, QPushButton, QTextEdit, QMenuBar, QAction, QFileDialog, QApplication

import core

current_version = '1.0'
auto_update_server = 'http://redino.net'

def getCurrentDirectory():
    return os.path.dirname(getExecutablePath())

def getExecutablePath():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(inspect.getfile(inspect.currentframe()))

def getLatestVersion():
	try:
		r = urllib.request.urlopen('{0}/updates/get_latest_version.php?app_name=ftp-git'.format(auto_update_server))
	except urllib.error.URLError:
		# use current version if updating server is not available
		return 0
	return r.read()
def isNewVersionAvailable():
	latest_version = getLatestVersion()
	return latest_version > current_version

class GitFtpWindow(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.setWindowTitle('Ftp-Git')

class AboutWindow(GitFtpWindow):
	def __init__(self):
		GitFtpWindow.__init__(self)
		vbox = QVBoxLayout()
		self.setLayout(vbox)

		label = QLabel('<b style="font-size:30px;">Ftp-Git</b>')
		vbox.addWidget(label)
		vbox.addWidget(QLabel('Copyright redino.net (gbstack08@gmail.com)'))
		link_btn = QCommandLinkButton('redino.net')
		link_btn.clicked.connect(self.websiteLinkClicked)
		vbox.addWidget(link_btn)

	def websiteLinkClicked(self):
		webbrowser.open_new_tab('http://redino.net')

class MainWindow(GitFtpWindow):
	def notifyError(self, text, title='Error'):
		msg_box = QMessageBox()
		msg_box.setWindowTitle('Error')
		msg_box.setText("Selected path is not a valid git repository")
		msg_box.exec_()

	app = core.Application()

	def __init__(self):
		GitFtpWindow.__init__(self)

		self.app.initDB()
		self.changed_files_model = QStandardItemModel()
		
		self.buildUI()
		self.getChangedFiles('.')

		# check new version
		if isNewVersionAvailable():
			msg_box = QMessageBox()
			msg_box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
			msg_box.setWindowTitle('Ftp-Git')
			msg_box.setText('New version of Ftp-Git is available. Do you want to download the new version?')
			ret = msg_box.exec_()
			if ret == QMessageBox.Yes:
				webbrowser.open_new_tab('http://redino.net/ftp-git')

	def buildUI(self):
		self.setFixedWidth(800)
		self.setFixedHeight(350)
		
		grid_layout = QGridLayout()
		self.setLayout(grid_layout)

		# Changed files table
		changed_files_table = QTableView()
		self.changed_files_table = changed_files_table
		changed_files_table.horizontalHeader().hide()
		grid_layout.addWidget(changed_files_table, 2, 0, 6, 3)
		changed_files_table.setModel(self.changed_files_model)

		# ftp part UI
		address_label = QLabel('Server Address')
		self.address_edit = QLineEdit()
		username_label = QLabel('Username')
		self.username_edit = QLineEdit()
		password_label = QLabel('Password')
		self.password_edit = QLineEdit()
		self.password_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
		upload_btn = QPushButton('Upload')
		base_dir_label = QLabel('Base Directory')
		self.base_dir_edit = QLineEdit()
		upload_btn.clicked.connect(self.uploadBtnClicked)

		# log console
		console_label = QLabel('Log')
		grid_layout.addWidget(console_label, 5,3,1,1)
		self.console_box = QTextEdit()
		# self.console_box.setFixedHeight(100)
		grid_layout.addWidget(self.console_box, 6, 3, 1, 5)
		
		# build menu bar
		menu_bar = QMenuBar()
		grid_layout.addWidget(menu_bar, 0,0,1,7)
		file_menu = menu_bar.addMenu('File')
		exit_action = QAction('Exit', self)
		exit_action.triggered.connect(sys.exit)
		file_menu.addAction(exit_action)

		donate_action = QAction('Donate', self)
		donate_action.triggered.connect(self.donateClicked)
		menu_bar.addAction(donate_action)

		help_menu = menu_bar.addMenu('Help')
		report_action = QAction('Report a bug', self)
		about_action = QAction('About', self)
		about_action.triggered.connect(self.aboutClicked)
		report_action.triggered.connect(self.reportClicked)
		help_menu.addAction(report_action)
		help_menu.addAction(about_action)

		grid_layout.addWidget(address_label, 1, 3, 1, 1)
		grid_layout.addWidget(self.address_edit, 1, 4, 1, 1)
		grid_layout.addWidget(username_label, 2, 3, 1, 1)
		grid_layout.addWidget(self.username_edit, 2, 4, 1, 1)
		grid_layout.addWidget(password_label, 3, 3, 1, 1)
		grid_layout.addWidget(self.password_edit, 3, 4, 1, 1)
		grid_layout.addWidget(base_dir_label, 4, 3, 1, 1)
		grid_layout.addWidget(self.base_dir_edit, 4, 4, 1, 1)
		grid_layout.addWidget(upload_btn, 5, 3, 1, 1)
		
		# repository path UI
		dir_label = QLabel('Repository path')
		grid_layout.addWidget(dir_label, 1,0,1,1)
		self.dir_edit = QLineEdit()
		self.dir_edit.setText(getCurrentDirectory())
		grid_layout.addWidget(self.dir_edit, 1,1,1,1)
		dir_btn = QPushButton('Choose')
		dir_btn.clicked.connect(self.chooseRepositoryPathBtnClicked)
		grid_layout.addWidget(dir_btn, 1,2,1,1)

		ftp_credentials = self.app.getFtpCredentials()
		if ftp_credentials:
			self.address_edit.setText(ftp_credentials[1])
			self.username_edit.setText(ftp_credentials[2])
			self.password_edit.setText(ftp_credentials[3])

	def donateClicked(self):
		webbrowser.open_new_tab('https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=FEBRQN6ZT5FKQ')
	def aboutClicked(self):
		self.about_window = AboutWindow()
		self.about_window.show()
	def reportClicked(self):
		webbrowser.open_new_tab('http://redino.net/forum')

	def getChangedFiles(self, repo_path):
		# get changed files
		try:
			r = git.Repo(repo_path)
			self.repo_path = repo_path
			self.dir_edit.setText(repo_path)
			self.changed_files_model.clear()
		except git.exc.InvalidGitRepositoryError:
			msg_box = QMessageBox()
			msg_box.setWindowTitle('Error')
			msg_box.setText("Selected path is not a valid git repository")
			msg_box.exec_()
			return
		c = r.head.commit
		self.changed_files = [os.path.join(self.repo_path, f) for f in list(c.stats.files.keys())]
		for f in list(c.stats.files.keys()):
			print(f)
			self.changed_files_model.appendRow([QStandardItem(f)])
		self.changed_files_table.setColumnWidth(0, self.changed_files_table.width())

	def chooseRepositoryPathBtnClicked(self):
		file_dlg = QFileDialog(self)
		file_dlg.setFileMode(QFileDialog.Directory)
		if file_dlg.exec_():
			files = file_dlg.selectedFiles()
			print(files)
			self.getChangedFiles(files[0])

	def printTextToConsole(self, text):
		print(text)
		original_text = self.console_box.toPlainText()
		self.console_box.setText(original_text+text+'\n')
	def displayError(self, text):
		msg_box = QMessageBox()
		msg_box.setWindowTitle('Error')
		msg_box.setText(text)
		msg_box.exec_()



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
		self.upload_thread = UploadThread(self)
		self.upload_thread.updateConsole.connect(self.printTextToConsole)
		self.upload_thread.updateConsoleError.connect(self.displayError)
		self.upload_thread.start()


class UploadThread(QThread):
	updateConsole = Signal(str)
	updateConsoleError = Signal(str)

	def __init__(self, window):
		QThread.__init__(self)
		self.window = window
		print(self.window)

	def run(self):
		server_address = self.window.address_edit.text()
		username = self.window.username_edit.text()
		password = self.window.password_edit.text()
		base_dir = self.window.base_dir_edit.text()

		ftp = ftplib.FTP()
		try:
			print(ftp.connect(server_address))
		except Exception as e:
			print(e)
			self.updateConsoleError.emit('Cannot connect to host')
			#self.window.printTextToConsole('Cannot connect to host')
			return

		try:
			self.updateConsole.emit('Authenticating..')
			login_status = ftp.login(username, password)
			self.updateConsole.emit(login_status)
			#self.window.printTextToConsole(login_status)
		except Exception as e:
			print(e)
			self.updateConsoleError.emit('login failed')
			return
			#self.window.printTextToConsole('login failed')

		for filename in self.window.changed_files:
			f = open(filename)
			self.updateConsole.emit(ftp.storlines('STOR '+os.path.join(base_dir, filename), f))
			#self.window.printTextToConsole(ftp.storlines('STOR '+filename, f))
			f.close()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()