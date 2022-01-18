import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
							QTableWidget, QComboBox, QTableWidgetItem,\
							QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,\
							QMainWindow, QCheckBox, QFileDialog, \
							QGridLayout, QDialog, QHeaderView, QAbstractItemView, \
							QDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore, QtGui, QtWidgets
#import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import random
import motors as m
import pandas as pd
import toggle as tg
import HEWLogger as hlog

class mover(QObject):
	finished = pyqtSignal()
	def add_params(self, ble):
		self.ble = ble

	def run(self):
		#print(self.ble.mono['monot'].name)
		self.ble.move_all()
		#self.bl.move_em(self.mvlist[0],self.mvlist[1],self.mvlist[2],self.mvlist[3],self.mvlist[4])
		print("Move Completed!")
		self.finished.emit()

class configView(QWidget):

	def __init__(self):
		super().__init__()

		self.thread = {}
		self.worker = {}

		self.master_df = pd.read_csv('data/BL_elements.csv', delimiter=',')
		#print(self.master_df.head())

		self.configs = QTableWidget()
		self.configs.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.configs.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.configs.verticalHeader().setVisible(False)
		self.configs.setSortingEnabled(True)
		self.configs.clicked.connect(self.print_config)
		self.configs.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
		self.configs.setWordWrap(True)

		self.new_btn = QPushButton("Create New Log")
		self.new_btn.clicked.connect(lambda: self.newFile())

		self.load_btn = QPushButton("Load Log File")
		self.load_btn.clicked.connect(lambda: self.get_config())

		self.move_btn = QPushButton("Restore Configuration")
		self.move_btn.clicked.connect(self.move_all)

		self.update_btn = QPushButton("Add Log Entry")
		self.update_btn.clicked.connect(self.update_log)

		self.refresh_btn = QPushButton("Refresh Log")
		self.refresh_btn.clicked.connect(lambda: self.get_config(load=False))


		self.initUI()


	def initUI(self):
		vbox = QVBoxLayout()
		vbox.addWidget(self.configs)

		hbox = QGridLayout()
		hbox.addWidget(self.new_btn, 0, 0)
		hbox.addWidget(self.load_btn, 0, 1)
		hbox.addWidget(self.move_btn, 1, 0)
		hbox.addWidget(self.update_btn, 1, 1)
		hbox.addWidget(self.refresh_btn, 0, 2)

		vbox.addLayout(hbox)
		self.setLayout(vbox)


	def get_config(self, load=True):
		if load==True:
			self.filename = QFileDialog.getOpenFileName(self,'Select File', '~/', "csv files (*.csv)")[0]
			self.new = True
		try:
			self.df = pd.read_csv(self.filename, delimiter=',')
			self.df = self.df.fillna('')
			self.build_table()
		except:
			print("Error loading CSV")

	def newFile(self):
		self.filename = str(QFileDialog.getSaveFileName()[0])
		self.new = False
		#connect to pandas code
		#self.bl = beamline_stats(self.filename, load=False)
		#self.loaded=1
		print(self.filename)

	def update_log(self):
		self.w = hlog.gui(self.filename, new = self.new)
		try:
			self.w = hlog.gui(self.filename, new = self.new)
		except:
			print("Error opening Logger - Have you opened a log file yet?")

	def build_table(self):
		nR, nC = self.df.shape
		#print("something")
		self.configs.setRowCount(nR)
		self.configs.setColumnCount(4)
		self.configs.setHorizontalHeaderLabels(("Date","Project","Energy","Comments"))
		tmp = self.df[['Date','Project','Energy (keV)','Comments']]

		#tmp.fillna('',inplace=True)
		for i in range(nR):
			for j in range(4):
				self.configs.setItem(i,j,QTableWidgetItem(str(tmp.iloc[i,j])))
		self.configs.resizeColumnsToContents()


	def print_config(self):
		row = self.configs.currentRow()
		#df = self.df.set_index('Date')
		#selected = self.df[]
		index = np.where(self.df['Date']==self.configs.item(row,0).text())[0][0]
		#keys = selected.columns
		#selected = selected.transpose()
		pstring="<table>"
		for key in self.df.columns:
			#print(selected.loc[key])
			val = self.df.loc[index, key]
			if val != '':
				if type(val) is str:
					pstring+="<tr><td><strong>%s</strong></td><td>%s</td></tr>" %(key, val)
				else:
					pstring+="<tr><td><strong>%s</strong></td><td>%.4g</td></tr>" %(key, val)
			#print(selected.loc[key])
		pstring+="</table>"
		print(pstring)
		self.config = self.df.loc[index]
		#print(df[self.configs.item(row,0).text()])

	def move_all(self):
		df = self.master_df[self.master_df['Category']=='mono']
		self.mon = m.mono()

		for key in df['Name']:
			i = df.index[df['Name']==key].to_list()[0]
			self.mon.set_pos(df.iloc[i]['label'], float(self.config[key]))

		df = self.master_df[self.master_df['Category']=='table']
		#print(df.head())
		self.tbl = m.table()
		#print(self.config['Trans Table Yaw'])
		for key in df['Name']:

			self.tbl.set_pos(self.master_df.iloc[i]['label'], float(self.config[key]))


		self.do_move(self.mon, 0)
		self.do_move(self.tbl, 1)

	def do_move(self, ble, i):

		self.thread[i] = QThread()
		self.worker[i] = mover()
		self.worker[i].add_params(ble)
		self.worker[i].moveToThread(self.thread[i])
		self.thread[i].started.connect(self.worker[i].run)
		self.worker[i].finished.connect(self.thread[i].quit)
		self.worker[i].finished.connect(self.worker[i].deleteLater)
		self.thread[i].finished.connect(self.thread[i].deleteLater)
		self.thread[i].start()









class restore_prep(QDialog):
	def __init__(self, df):
		super().__init__()


		self.set_HE = tg.AnimatedToggle(checked_color='#9812e0', pulse_checked_color="#449812e0")
		self.set_HE.setFixedSize(self.set_HE.sizeHint())

		self.set_s1 = tg.AnimatedToggle(checked_color='#9812e0', pulse_checked_color="#449812e0")
		self.set_s1.setFixedSize(self.set_s1.sizeHint())

		self.set_s2 = tg.AnimatedToggle(checked_color='#9812e0', pulse_checked_color="#449812e0")
		self.set_s2.setFixedSize(self.set_s2.sizeHint())

		self.set_bs = tg.AnimatedToggle(checked_color='#9812e0', pulse_checked_color="#449812e0")
		self.set_bs.setFixedSize(self.set_bs.sizeHint())
