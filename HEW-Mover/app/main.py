import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
							QApplication, QToolTip, QDesktopWidget,\
						 	QLabel, QHBoxLayout, QVBoxLayout, QTextEdit,\
							QMainWindow, QTabWidget, QFileDialog, \
							QGridLayout
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore, QtGui, QtWidgets
import mover as mv
import configs as cf
import bragg_calc as bg
import os


class MyStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class biggui(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		tabs = QTabWidget()
		sys.stdout = MyStream(textWritten=self.normalOutputWritten)
		self.textEdit=QTextEdit(self)
		self.textEdit.setReadOnly(True)
		self.textEdit.insertHtml('<h2>BXDS-HEW Beamline Toolkit</h2> ')
		self.textEdit.insertPlainText('\nWritten by Al Rahemtulla\n')
		tab = mv.PositionCal()
		tab2 = cf.configView()
		tab3 = bg.BraggCalc()
		#tab4 = pos.PositionCal()


		tabs.addTab(tab, "Beamline Positions")
		tabs.setFixedWidth(400)
		tabs.addTab(tab2, "Configurations")
		tabs.addTab(tab3, "Calculator")

		#tabs.addTab(tab, "Function Fitter")

		hbox = QHBoxLayout()
		hbox.addWidget(tabs)
		hbox.addWidget(self.textEdit)
		self.setLayout(hbox)
	def normalOutputWritten(self, text):
		"""Append text to the QTextEdit."""
		# Maybe QTextEdit.append() works as well, but this is how I do it:
		cursor = self.textEdit.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		if text[0]=='<':
			self.textEdit.insertHtml(text)
			self.textEdit.insertPlainText('\n')
		else:
			self.textEdit.insertPlainText(text)
		cursor.movePosition(QtGui.QTextCursor.End)
		self.textEdit.setTextCursor(cursor)
		self.textEdit.ensureCursorVisible()
	def __del__(self):
		# Restore sys.stdout
		sys.stdout = sys.__stdout__

class gui(QMainWindow):
	def __init__(self):
		super(gui, self).__init__()

		self.initUI()

	def initUI(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		tabs = biggui()
		self.resize(800,500)
		self.setWindowTitle('HEW Toolkit')
		self.setWindowIcon(QtGui.QIcon(dir_path+'/../data/logo_2.png'))

		self.setCentralWidget(tabs)
		self.show()

def main():

	app = QApplication(sys.argv)
	app.processEvents()

	w = gui()


	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
