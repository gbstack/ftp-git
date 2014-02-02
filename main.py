from PySide.QtCore import *
from PySide.QtGui import *
import sys
import git

class MainWindow(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		grid_layout = QGridLayout()
		self.setLayout(grid_layout)

		changed_files_table = QTableView()
		grid_layout.addWidget(changed_files_table, 0, 0, 1, 1)
		changed_files_model = QStandardItemModel()

		r = git.Repo('.')
		c = r.head.commit
		for f in c.stats.files:
			changed_files_model.appendRow([QStandardItem(f)])

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()