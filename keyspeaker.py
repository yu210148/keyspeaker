#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Project: keyspeaker
# Description: A Qt5 frontend for espeak-ng
# Author: Kevin Lucas <yu210148@gmail.com>
# Copyright: 2020
# License: GPL-3+
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 3 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
# UI Created by: PyQt5 UI code generator 5.11.3
#

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence
import subprocess, os, signal, re, pathlib, sys, atexit

# set a default value for speakerProcess so the thing doesn't crash if pause is pressed before play
speakerProcess = False
#global variable here to control the pause button labeling
fPaused = False

def get_list_of_espeak_voices():
    # returns a list of values passable to espeak-ng -v xxx to adjust language & voice
    
    voiceNames = []
    process = subprocess.run(["espeak-ng", "--voices"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    
    voices = output.splitlines()
    for voice in voices:
        #print (voice)
        name = re.split("(\s+)", voice)
        #print (name[4])
        voiceNames.append(name[4])
    
    #remove the first element from the list that contains the header
    voiceNames.pop(0)
    return voiceNames

def get_list_of_mbrola_voices():
    # GET A LIST OF MBROLA VOICES IN THE SAME WAY AS THE ESPEAK ONES ABOVE
    
    path = '/usr/lib/x86_64-linux-gnu/espeak-ng-data/voices/mb'
    try:
        mbVoices = os.listdir(path)
    except:
        mbVoices = [] #if no mbrola voices found return empty list
    return mbVoices
    
voiceNames = get_list_of_espeak_voices()
mbVoices = get_list_of_mbrola_voices()
mbVoices.sort()
voiceNames.sort()
allVoices = mbVoices + voiceNames

# allVoices now contains a list of the possible options to pass to espeak-ng

def check_if_speaking():
    # function to check if there's already a speaking process
    # returns True if there is and False if not
    try:
        if speakerProcess.poll() is None:
            return True
        else:
            return False
    except:
        return False

def check_voice_file():
    # a function to check if the ~/.config/keyspeaker/voice.conf exists
    # returns the voice to use or False
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker' / 'voice.conf')
    
    if fExists is False:
        return False
    else:
        # try to open the file and get the value
        try:
            f = open(pathlib.Path.home() / '.config' / 'keyspeaker' / 'voice.conf')
        except:
            return False
        voice = f.read() # voice vile consists of a single line with the voice to use
        return voice

def set_voice_file(voice):
    # a function to write the currently set voice to ~/.config/keyspeaker/voice.conf
    # for persistance
    fExists = os.path.exists(pathlib.Path.home() / '.config')
    
    # if ~/.config doesn't exist create it
    if fExists is False:
        # CREATE ~/.config directory
        os.makedirs(pathlib.Path.home() / '.config')
    
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker')
    
    # if ~/.config/keyspeaker doesn't exist create is
    if fExists is False:
        # CREATE ~/.config/keyspeaker
        os.makedirs(pathlib.Path.home() / '.config' / 'keyspeaker')
    
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker' / 'voice.conf')
    
    # if ~/.config/keyspeaker/rate.conf exists, remove it 
    if fExists is True:
        os.remove(pathlib.Path.home() / '.config' / 'keyspeaker' / 'voice.conf')
    
    # write a new rate.conf with the current rate value
    file = open(pathlib.Path.home() / '.config' / 'keyspeaker' / 'voice.conf', 'w+')
    file.write(voice)

def check_rate_file():
    # a function to check if the ~/.config/keyspeaker/rate.conf
    # returns the rate to use if present and False if it doesn't exist
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker' / 'rate.conf')
    
    if fExists is False:
        return False
    else:
        # try to open the file and get the value
        try:
            f = open(pathlib.Path.home() / '.config' / 'keyspeaker' / 'rate.conf')
        except:
            return False
        rate = f.read() # rate file consists of a single line with the number to use
        return rate
        
def set_rate_file(rate):
    # a function to write the currently set rate to ~/.config/keyspeaker/rate.conf
    # for data persistance
    fExists = os.path.exists(pathlib.Path.home() / '.config')
    
    # if ~/.config doesn't exist create it
    if fExists is False:
        # CREATE ~/.config directory
        os.makedirs(pathlib.Path.home() / '.config')
    
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker')
    
    # if ~/.config/keyspeaker doesn't exist create is
    if fExists is False:
        # CREATE ~/.config/keyspeaker
        os.makedirs(pathlib.Path.home() / '.config' / 'keyspeaker')
    
    fExists = os.path.exists(pathlib.Path.home() / '.config' / 'keyspeaker' / 'rate.conf')
    
    # if ~/.config/keyspeaker/rate.conf exists, remove it 
    if fExists is True:
        os.remove(pathlib.Path.home() / '.config' / 'keyspeaker' / 'rate.conf')
    
    # write a new rate.conf with the current rate value
    file = open(pathlib.Path.home() / '.config' / 'keyspeaker' / 'rate.conf', 'w+')
    file.write(rate)

def stop_talking():
    try:
        os.kill(speakerProcess.pid, signal.SIGKILL)
    except:
        pass
    
#Button Handlers
def on_play_button_clicked(text, self):
    # write the rate and voice to a conf file so that the user's selctions
    # persist across sessions
    rate = str(self.rateSlider.value())
    set_rate_file(rate)
    
    voice = str(self.VoiceComboBox.currentText())
    set_voice_file(voice)
    
    global speakerProcess
    
    fIsSpeaking = check_if_speaking()
    
    # if currently speaking stop the current speaking and start with what's in the text box
    if fIsSpeaking is True:
        stop_talking()
        # if the fIsSpeaking is true but playback is paused this will change the resume button back to pause 
        self.pauseButton.setText("Pause")
        icon = QtGui.QIcon.fromTheme("media-playback-pause")
        self.pauseButton.setIcon(icon)
        global fPaused
        fPaused = False

    if voice == 'Default':
            speakerProcess = subprocess.Popen(["espeak-ng", "-s", rate, text])
    else:
            speakerProcess = subprocess.Popen(["espeak-ng", "-s", rate, "-v", voice, text])

def on_pause_button_clicked(self):
    global fPaused
    
    if (fPaused == False):
        # halt the speaking process
        try:
            os.kill(speakerProcess.pid, signal.SIGSTOP)
        except:
            pass
        
        # and change the button marking to 'resume'
        self.pauseButton.setText("Resume")
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.pauseButton.setIcon(icon)
        
        # set value of fPaused to true
        fPaused = True
    
    else:
        # resume the speaking process
        try:
            os.kill(speakerProcess.pid, signal.SIGCONT)
        except:
            pass
        
        # and change the buton marking to 'pause'
        self.pauseButton.setText("Pause")
        icon = QtGui.QIcon.fromTheme("media-playback-pause")
        self.pauseButton.setIcon(icon)
        
        # set value of fPaused to false
        fPaused = False

def on_stop_button_clicked(self):
    # kill the speaking process
    try:
        os.kill(speakerProcess.pid, signal.SIGKILL)
    except:
        pass
    # and change the button marking for 'pause'
    self.pauseButton.setText("Pause")
    icon = QtGui.QIcon.fromTheme("media-playback-pause")
    self.pauseButton.setIcon(icon)
    
    # set value of fPaused to false
    global fPaused
    fPaused = False

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(806, 684)
        #MainWindow.resize(640, 480)
        MainWindow.resize(300, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setPlainText("Welcome to Keyspeaker.\n"
            "Paste the text you'd like to have spoken into this window\n"
            "and I'll speak it when you press the play button below.\n")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.playButton = QtWidgets.QPushButton(self.centralwidget)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.playButton.setIcon(icon)
        self.playButton.setObjectName("&playButton")
        self.gridLayout_2.addWidget(self.playButton, 0, 0, 1, 1)
        self.pauseButton = QtWidgets.QPushButton(self.centralwidget)
        icon = QtGui.QIcon.fromTheme("media-playback-pause")
        self.pauseButton.setIcon(icon)
        self.pauseButton.setObjectName("p&auseButton")
        self.gridLayout_2.addWidget(self.pauseButton, 0, 1, 1, 1)
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        icon = QtGui.QIcon.fromTheme("media-playback-stop")
        self.stopButton.setIcon(icon)
        self.stopButton.setObjectName("&stopButton")
        self.gridLayout_2.addWidget(self.stopButton, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.rateLabel = QtWidgets.QLabel(self.centralwidget)
        self.rateLabel.setObjectName("rateLabel")
        self.gridLayout_3.addWidget(self.rateLabel, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rateSlider = QtWidgets.QSlider(self.centralwidget)
        self.rateSlider.setMinimum(80)
        self.rateSlider.setMaximum(390)
        
        # check conf file to see what the last rate and voice setting was and
        # use those values if they exist to set initial values for the gui
        rate = check_rate_file()
        if rate is False:
            rate = 262
        voiceToUse = check_voice_file()
        if voiceToUse is False:
            voiceToUse = 'Default'
            
        self.rateSlider.setSliderPosition(int(rate))
        self.rateSlider.setOrientation(QtCore.Qt.Horizontal)
        self.rateSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.rateSlider.setObjectName("rateSlider")
        self.horizontalLayout.addWidget(self.rateSlider)
        self.rateSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.rateSpinBox.setMinimum(80)
        self.rateSpinBox.setMaximum(390)
            
        self.rateSpinBox.setProperty("value", rate)
        self.rateSpinBox.setObjectName("rateSpinBox")
        self.horizontalLayout.addWidget(self.rateSpinBox)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 1, 0, 1, 1)
        
        self.VoiceLabel = QtWidgets.QLabel(self.centralwidget)
        self.VoiceLabel.setObjectName("VoiceLabel")
        self.gridLayout_4.addWidget(self.VoiceLabel, 2, 0, 1, 1)
        
        self.VoiceComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.VoiceComboBox.setObjectName("VoiceComboBox")
        
        self.VoiceComboBox.addItem("")
        self.VoiceComboBox.setItemText(0, "Default")
        
        # insert voice options into drop-down
        i = 1
        for voice in allVoices:
            self.VoiceComboBox.addItem("")
            self.VoiceComboBox.setItemText(i, voice)
            i = i + 1
        
        # check ~/.config/keyspeaker/voice.conf and select that voice by default
        index = self.VoiceComboBox.findText(voiceToUse, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.VoiceComboBox.setCurrentIndex(index)
        
        self.gridLayout_4.addWidget(self.VoiceComboBox, 3, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 806, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        
        # Keyboard shortcut for quit
        self.actionQuit.setShortcut('Ctrl+Q')
        self.actionQuit.triggered.connect(app.quit)
        
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        #self.menubar.addAction(self.menuEdit.menuAction())
        self.retranslateUi(MainWindow)
        self.rateSlider.valueChanged['int'].connect(self.rateSpinBox.setValue)
        self.rateSpinBox.valueChanged['int'].connect(self.rateSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #Connect Buttons to function calls
        self.playButton.clicked.connect(lambda: on_play_button_clicked(self.textEdit.toPlainText(), self))
        self.pauseButton.clicked.connect(lambda: on_pause_button_clicked(self))
        self.stopButton.clicked.connect(lambda: on_stop_button_clicked(self))
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Keyspeaker"))
        self.playButton.setText(_translate("MainWindow", "Play"))
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.rateLabel.setText(_translate("MainWindow", "Speach Rate:"))
        
        self.VoiceLabel.setToolTip(_translate("MainWindow", "<html><head/><body><p>Note: All Languages here may not be installed. If you select one that isn\'t a default will be used.</p></body></html>"))
        self.VoiceLabel.setText(_translate("MainWindow", "Voice / Language"))
        
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        #self.menuEdit.setTitle(_translate("MainWindow", "&Edit"))
        self.actionQuit.setText(_translate("MainWindow", "&Quit"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowIcon(QtGui.QIcon('keyspeaker.png'))
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # STOP PLAYBACK WHEN PROGRAM IS CLOSED
    atexit.register(stop_talking)
    sys.exit(app.exec_())
