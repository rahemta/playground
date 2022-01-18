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
import pandas as pd

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

class Filter(QWidget):

	def __init__(self):
		super().__init__()

		df = pd.read_csv(dir_path+'/../data/filter_wheel.csv', delimiter=',')
		self.fw_dict = df.set_index('Filter')['Position'].to_dict()
		self.fw = QComboBox()
		for key in self.fw_dict:
			self.fw.addItem(key)

		self.move = QPushButton('Set Filter')
		self.move.clicked.connect(lambda: self.change_filter())
		self.mot = m.motor('Filter Wheel', 'SMTR1604-3-I22-07', 'deg', 'sp')

		self.initUI()

	def initUI(self):

		hbox = QHBoxLayout()
		hbox.addWidget(QLabel('Select Filter'))
		hbox.addWidget(self.fw)
		hbox.addWidget(self.move)
		self.setLayout(hbox)


	def change_filter(self):
		pos = self.fw_dict[self.fw.currentText()]
		self.mot.move_motor(pos)
