#!/usr/bin/env python
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
							QTableWidget, QComboBox, QTableWidgetItem,\
						 	QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,\
							QMainWindow, QCheckBox, QFileDialog, \
							QGridLayout, QDialog, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore, QtGui, QtWidgets
#import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import random
import motors as m
import filter as f

#from . import beamline_calc_new as bl
#from . import bragg_calc as bc
#from . import toggle as tg

class mover(QObject):
	finished = pyqtSignal()
	def add_params(self, ble):
		self.ble = ble

	def run(self):
		#print(self.ble.mono['monot'].name)
		self.ble.move_all()
		#self.bl.move_em(self.mvlist[0],self.mvlist[1],self.mvlist[2],self.mvlist[3],self.mvlist[4])
		#print("Move Completed!")
		self.finished.emit()


class PositionCal(QWidget):


	def __init__(self):
		super().__init__()

		self.thread = {}
		self.worker = {}

		self.energy = QLineEdit('35')
		self.energy.setFixedSize(100,25)

		self.mono = QComboBox()
		self.mono.addItem("111")
		self.mono.addItem("422")
		self.mono.addItem("533")


		self.ref = m.energy()
		self.mono.currentTextChanged.connect(self.change_mono)


		#self.ot_in = tg.AnimatedToggle(checked_color='#9812e0', pulse_checked_color="#449812e0")
		#self.ot_in.setFixedSize(self.ot_in.sizeHint())
		#self.ot_in.setChecked(True)

		self.calc_btn = QPushButton("Calculate")
		self.calc_btn.setFixedSize(100,25)
		self.calc_btn.clicked.connect(lambda: self.calc_pos())
		self.safe_btn = QPushButton("Move")
		self.safe_btn.clicked.connect(lambda: self.full_move())

		self.filter = f.Filter()


		self.pos = TableWidget(('Mono', 'Table Yaw', 'Table US', 'Table DS'),\
								('Motor Val', 'Energy (keV)'))
		self.pos.setFixedSize(350,81)
		self.pos.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.pos.setSelectionMode(QAbstractItemView.NoSelection)


		self.flux = TableWidget(('Ring', 'IOC1', 'IOC2', 'Spare'), ['Val'])
		self.flux.setFixedSize(350,51)
		self.flux.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.flux.setSelectionMode(QAbstractItemView.NoSelection)

		self.update_timer = QtCore.QTimer(self)
		self.update_timer.setInterval(1000)
		self.update_timer.timeout.connect(lambda: self.getVal(self.ref.cal))
		self.update_timer.start(1000)





		self.initUI()

	def initUI(self):

		grid = QGridLayout()
		grid.addWidget(QLabel("Input Energy (keV)") , 0, 0)
		grid.addWidget(self.energy, 0, 1)
		grid.addWidget(QLabel("Select Mono Reflection"), 1, 0)
		grid.addWidget(self.mono, 1, 1)

		grid.addWidget(self.calc_btn,0,2)
		grid.addWidget(self.safe_btn,1,2)
		sep = QtWidgets.QFrame()

		vbox = QVBoxLayout()
		vbox.addLayout(grid)
		vbox.addWidget(self.filter)
		#vbox.addStretch(1)
		sep2 = QtWidgets.QFrame()
		sep.setFrameShape(QtWidgets.QFrame.HLine)
		vbox.addWidget(sep)
		vbox.addWidget(QLabel("Beamline Feedback"))
		vbox.addWidget(self.pos)
		vbox.addWidget(sep2)
		vbox.addWidget(self.flux)
		#vbox.addLayout(grid2)
		vbox.addStretch(1)
		self.setLayout(vbox)






	def calc_pos(self):
		try:
			energy = float(self.energy.text())

			self.ref.calc(energy)
		except ValueError:
			print("Invalid Value for Energy.")

	def full_move(self):
		energy = float(self.energy.text())
		self.ref.calc(energy, disp=False)

		self.mon = m.mono()
		for key in self.mon.mono:
			self.mon.set_pos(key, self.ref.pos[key])

		self.tbl = m.table()
		for key in self.tbl.table:
			self.tbl.set_pos(key, self.ref.pos[key])

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

	def getVal(self, df) -> None:

		#val = float(self.item(0,0).text())
		#Will Become and EPICS gets
		val = -1.331+random.uniform(-0.01,0.01)
		self.pos.setItem(0,0,QTableWidgetItem("{0:.5g}".format(val)))
		val = 11.41+random.uniform(-0.1,0.1)
		self.pos.setItem(0,1,QTableWidgetItem("{0:.5g}".format(val)))
		val = 0.5+random.uniform(-0.01,0.01)
		self.pos.setItem(0,2,QTableWidgetItem("{0:.5g}".format(val)))
		val = 2.133+random.uniform(-0.01,0.01)
		self.pos.setItem(0,3,QTableWidgetItem("{0:.5g}".format(val)))

		val = m.calc_asin_inv(float(self.pos.item(0,0).text()),df.loc['monoth','Fit_A'], df.loc['monoth','Fit_B'])
		#print(val)
		self.pos.setItem(1,0,QTableWidgetItem("{0:.5g}".format(val)))
		val = m.calc_lin_inv(float(self.pos.item(0,1).text()),df.loc['tyaw','Fit_A'], df.loc['tyaw','Fit_B'])
		val = m.calc_asin_inv(val,df.loc['monoth','Fit_A'], df.loc['monoth','Fit_B'])
		self.pos.setItem(1,1,QTableWidgetItem("{0:.5g}".format(val)))

		val = m.calc_lin_inv(float(self.pos.item(0,1).text()),df.loc['tus','Fit_A'], df.loc['tus','Fit_B'])
		val = m.calc_asin_inv(val,df.loc['monoth','Fit_A'], df.loc['monoth','Fit_B'])
		self.pos.setItem(1,2,QTableWidgetItem("{0:.5g}".format(val)))

		val = m.calc_lin_inv(float(self.pos.item(0,1).text()),df.loc['tds','Fit_A'], df.loc['tds','Fit_B'])
		val = m.calc_asin_inv(val,df.loc['monoth','Fit_A'], df.loc['monoth','Fit_B'])
		self.pos.setItem(1,3,QTableWidgetItem("{0:.5g}".format(val)))

		#Flux
		val = random.uniform(-1,1)+217
		self.flux.setItem(0,0,QTableWidgetItem("{0:.4g}".format(val)))
		val = random.uniform(-2e-7,2e-7)+1.3e-6
		self.flux.setItem(0,1,QTableWidgetItem("{0:.4g}".format(val)))
		val = random.uniform(-1e-7,1e-7)+4.3e-7
		self.flux.setItem(0,2,QTableWidgetItem("{0:.4g}".format(val)))
		val = random.uniform(-1e-13,1e-13)+1.3e-12
		self.flux.setItem(0,3,QTableWidgetItem("{0:.4g}".format(val)))


	def change_mono(self):
		mono = self.mono.currentText()
		self.ref = m.energy(mono=mono)

class TableWidget(QTableWidget):
	def __init__(self, hlabel, vlabel):
		super().__init__()

		self.setColumnCount(len(hlabel))
		self.setRowCount(len(vlabel))
		self.setHorizontalHeaderLabels(hlabel)
		if len(vlabel)>1:
			self.setVerticalHeaderLabels(vlabel)
		else:
			self.verticalHeader().setVisible(False)


		#self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		for i in range(len(vlabel)):
			for j in range(len(hlabel)):
				self.setItem(i,j,QTableWidgetItem(str(random.randint(0,100))))
