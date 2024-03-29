from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(518, 505)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_1.setObjectName("verticalLayout_1")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_1 = QtWidgets.QGridLayout()
        self.gridLayout_1.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_1.setObjectName("gridLayout_1")
        self.verticalLayout_2.addLayout(self.gridLayout_1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.ClientStartBtn = QtWidgets.QPushButton(self.tab_1)
        self.ClientStartBtn.setObjectName("ClientStartBtn")
        self.horizontalLayout_2.addWidget(self.ClientStartBtn)
        self.ClientStopBtn = QtWidgets.QPushButton(self.tab_1)
        self.ClientStopBtn.setObjectName("ClientStopBtn")
        self.horizontalLayout_2.addWidget(
            self.ClientStopBtn, 0, QtCore.Qt.AlignRight)
        self.ClientSkipAudio = QtWidgets.QPushButton(self.tab_1)
        self.ClientSkipAudio.setObjectName("ClientSkipAudio")
        self.horizontalLayout_2.addWidget(self.ClientSkipAudio)
        self.ClientRemoveAudio = QtWidgets.QPushButton(self.tab_1)
        self.ClientRemoveAudio.setObjectName("ClientRemoveAudio")
        self.horizontalLayout_2.addWidget(self.ClientRemoveAudio)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem2)
        self.label_2 = QtWidgets.QLabel(self.tab_1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.log_window2 = QtWidgets.QPlainTextEdit(self.tab_1)
        sizePolicy2 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.log_window2.sizePolicy().hasHeightForWidth())
        self.log_window2.setSizePolicy(sizePolicy2)
        self.log_window2.setAutoFillBackground(False)
        self.log_window2.setReadOnly(True)
        self.log_window2.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.log_window2.setObjectName("log_window2")
        self.log_window2.setFixedHeight(100)
        self.verticalLayout_2.addWidget(self.log_window2)
        self.label_1 = QtWidgets.QLabel(self.tab_1)
        self.label_1.setObjectName("label_1")
        self.verticalLayout_2.addWidget(self.label_1)
        self.log_window = QtWidgets.QPlainTextEdit(self.tab_1)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.log_window.sizePolicy().hasHeightForWidth())
        self.log_window.setSizePolicy(sizePolicy)
        self.log_window.setAutoFillBackground(False)
        self.log_window.setReadOnly(True)
        self.log_window.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.log_window.setObjectName("log_window")
        self.verticalLayout_2.addWidget(self.log_window)
        self.tabWidget.addTab(self.tab_1, "")
        self.verticalLayout_1.addWidget(self.tabWidget)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.statusbar = QtWidgets.QLabel(self.centralwidget)
        self.statusbar.setObjectName("statusbar")
        self.gridLayout_2.addWidget(
            self.statusbar, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.volumeSlider = QtWidgets.QSlider(
            Qt.Horizontal, self.centralwidget)
        self.gridLayout_2.addWidget(
            self.volumeSlider, 1, 0, 1, 0, QtCore.Qt.AlignRight)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 0, 1, 1, 1)
        self.verticalLayout_1.addLayout(self.gridLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ClientStartBtn.setText(_translate("MainWindow", "Start"))
        self.ClientStopBtn.setText(_translate("MainWindow", "Stop"))
        self.ClientSkipAudio.setText(_translate("MainWindow", "Skip current"))
        self.ClientRemoveAudio.setText(
            _translate("MainWindow", "Delete first"))
        self.label_1.setText(_translate("MainWindow", "Status:"))
        self.label_2.setText(_translate(
            "MainWindow", "Currently generated message:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_1), _translate("MainWindow", "TTS"))
        self.statusbar.setText(_translate("MainWindow", "Ready"))
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setTickInterval(10)
        self.volumeSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.volumeSlider.setValue(70)
