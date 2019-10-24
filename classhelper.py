import ctypes
import os
import pprint
import sys
from os.path import expanduser
from pathlib import Path, PurePosixPath


from PyQt5.QtCore import QDir, QSize, Qt, pyqtSlot
from PyQt5.QtGui import (QColor, QIcon, QKeySequence, QPalette, QStandardItem,
                         QStandardItemModel)

from utils import Settings, Setup, Ui_MainWindow, Dialog


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = Settings()
        self.load_settings = self.settings.settings
        self.load_settings

        lessons = sorted(self.settings.lesson_path.expanduser().glob(
            '**/*1-Lesson-Plans'))[0]
        lessons_dirs = [x for x in Path(lessons).iterdir() if x.is_dir()]
        for lesson in lessons_dirs:
            self.ui.lessonList.addItem(lesson.stem)
        self.ui.activityList.les_dirs = lessons_dirs
        self.show()

        self.class_repo = Path(
            self.settings.class_path, self.settings.class_day).expanduser()
        self.ui.activitiesDone.basePath = [
            x for x in self.class_repo.iterdir() if x.is_dir()]

        self.ui.radioButton.value = '1'
        self.ui.radioButton.setChecked(True)
        self.ui.radioButton.toggled.connect(self.radioClicked)
        self.ui.radioButton_2.value = '2'
        self.ui.radioButton_2.toggled.connect(self.radioClicked)
        self.ui.radioButton_3.value = '3'
        self.ui.radioButton_3.toggled.connect(self.radioClicked)
        self.radioClicked()

        self.ui.lessonList.currentIndexChanged.connect(self.radioClicked)

        self.ui.pushActivity.clicked.connect(self.pushActivity)

        if self.settings.theme == 'light':
            self.ui.action_Dark_Mode.setChecked(False)
            self.light_mode()
        elif self.settings.theme == 'dark':
            self.ui.action_Dark_Mode.setChecked(True)
            self.dark_mode()

        self.ui.action_Dark_Mode.changed.connect(self.theme_toggle)

        if self.settings.commit_msg == 'Lesson_Name - Solved':
            self.ui.actionLesson_Name_Solved.setChecked(True)
        elif self.settings.commit_msg == '00 - Solved':
            self.ui.action00_Solved.setChecked(True)
        elif self.settings.commit_msg == '00 - Lesson_name - Solved':
            self.ui.action00_Lesson_name_Solved.setChecked(True)

        self.ui.commit_group.triggered.connect(self.commit_msg)

        if self.settings.push_style == 'All Unsolved':
            self.ui.actionAll_Unsolved.setChecked(True)
        elif self.settings.push_style == 'One Activity':
            self.ui.actionOne_Activity.setChecked(True)

        self.ui.setup_group.triggered.connect(self.setup_style)

        self.ui.action_Set_Class_Repo.triggered.connect(self.select_dirs)

    def select_dirs(self):
        dirSelectWindow()
        daySelect()

    def radioClicked(self):
        '''
        Clears activity list.  Passes current lesson and day to update_activity/ignore_check.       
        '''
        if self.ui.radioButton.isChecked():
            radioButton = self.ui.radioButton
        elif self.ui.radioButton_2.isChecked():
            radioButton = self.ui.radioButton_2
        elif self.ui.radioButton_3.isChecked():
            radioButton = self.ui.radioButton_3
        self.ui.activityList.cur_les = self.ui.lessonList.currentIndex()
        self.ui.activityList.cur_day = radioButton.value
        self.ui.activityList.clear()
        self.update_activity()
        self.ignore_check()

    def update_activity(self):
        '''
        Joins path for current lesson/day with Lesson Plans activities directory.\n
        Iterates over child directories and populates activity selector.
        '''
        activity_l = self.ui.activityList
        try:
            act_path = Path(
                activity_l.les_dirs[activity_l.cur_les]) / activity_l.cur_day / 'Activities'
            activity_list = [x for x in act_path.iterdir() if x.is_dir()]
            for activity in activity_list:
                activity_l.addItem(activity.stem)
            activity_l.update()
        except FileNotFoundError:
            self.error_box

    def ignore_check(self):
        '''
        Parses lesson-level .gitignore and populates combo box with commented solved activities.


        Calculates lesson progess with a ratio of commented solved activities
        to uncommented solved activities.
        '''
        actDone = self.ui.activitiesDone
        cur_les = self.ui.activityList.cur_les
        cur_day = self.ui.activityList.cur_day
        model = QStandardItemModel()
        try:
            ignore_path = Path(actDone.basePath[cur_les]) / '.gitignore'

            with open(ignore_path.as_posix(), 'r') as gitignore:
                line_count = 0
                act_count = 0
                for line in gitignore.read().splitlines():
                    if line.startswith(cur_day) and line.endswith('Solved'):
                        line_count += 1
                    if line.startswith('#' + cur_day) and line.endswith('Solved'):
                        act_count += 1
                        act = line.split('/')[2]
                        model.appendRow(QStandardItem(act))
            try:
                progress = act_count / line_count * 100
            except ZeroDivisionError:
                progress = 100
            self.ui.lessonProgress.setValue(progress)
            QtWidgets.qApp.processEvents()
            self.ui.lessonProgress.update()
            actDone.setModel(model)
        except IndexError:
            self.error_box()

    def pushActivity(self):
        '''
        Ignores Activity and pushes
        '''
        self.radioClicked()
        self.settings.load_settings()
        lesson = self.ui.lessonList.currentText()
        day = self.ui.activityList.cur_day
        setup = Setup(lesson)
        setup.ignore_act(str(day), str(self.ui.activityList.currentText()))
        QtWidgets.qApp.processEvents()
        self.ui.lessonProgress.update()

    def error_box(self):
        '''Error dialog for missing paths'''
        error = QtWidgets.QMessageBox()
        error.setText('File path does not exist')
        error.setWindowTitle('Error')
        error.setIcon(QtWidgets.QMessageBox.Critical)
        error.exec_()

    def add_to_class(self):
        pass

    def commit_msg(self):
        '''Sets commit message value in settings'''
        active = self.ui.commit_group.checkedAction()
        print(active.text())
        self.settings.write('commitMsg', active.text())

    def setup_style(self):
        '''Sets weekly setup style in settings.json'''
        active = self.ui.setup_group.checkedAction()
        print(active.text())
        self.settings.write('pushStyle', active.text())

    def theme_toggle(self):
        '''Toggles theme'''
        if self.ui.action_Dark_Mode.isChecked():
            self.set_dark_mode()
        else:
            self.ui.action_Dark_Mode.setChecked(False)
            self.set_light_mode()

    def set_dark_mode(self):
        '''Writes dark theme to settings.json and calls dark mode palette'''
        self.settings.write('theme', 'dark')
        self.dark_mode()

    def set_light_mode(self):
        '''Writes light theme to settings.json and calls light mode palette'''
        self.settings.write('theme', 'light')
        self.light_mode()

    def dark_mode(self):
        '''Sets palette for dark mode'''
        darkMode = QPalette()
        darkMode.setColor(QPalette.Window, QColor(53, 53, 53))
        darkMode.setColor(QPalette.WindowText, Qt.white)
        darkMode.setColor(QPalette.Base, QColor(25, 25, 25))
        darkMode.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        darkMode.setColor(QPalette.ToolTipBase, Qt.white)
        darkMode.setColor(QPalette.ToolTipText, Qt.white)
        darkMode.setColor(QPalette.Text, Qt.white)
        darkMode.setColor(QPalette.Button, QColor(53, 53, 53))
        darkMode.setColor(QPalette.ButtonText, Qt.white)
        darkMode.setColor(QPalette.BrightText, Qt.red)
        darkMode.setColor(QPalette.Link, QColor(42, 130, 218))
        darkMode.setColor(QPalette.Highlight, QColor(42, 130, 218))
        darkMode.setColor(QPalette.HighlightedText, Qt.black)
        QtWidgets.qApp.processEvents()
        QtWidgets.qApp.setPalette(darkMode)

    def light_mode(self):
        '''Sets palette for light mode'''
        lightMode = QPalette()
        lightMode.setColor(QPalette.Window, QColor(245, 245, 245))
        lightMode.setColor(QPalette.WindowText, Qt.black)
        lightMode.setColor(QPalette.Base, QColor(245, 245, 245))
        lightMode.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        lightMode.setColor(QPalette.ToolTipBase, Qt.black)
        lightMode.setColor(QPalette.ToolTipText, Qt.black)
        lightMode.setColor(QPalette.Text, Qt.black)
        lightMode.setColor(QPalette.Button, QColor(245, 245, 245))
        lightMode.setColor(QPalette.ButtonText, Qt.black)
        lightMode.setColor(QPalette.BrightText, Qt.red)
        lightMode.setColor(QPalette.Link, QColor(42, 130, 218))
        lightMode.setColor(QPalette.Highlight, QColor(42, 130, 218))
        lightMode.setColor(QPalette.HighlightedText, Qt.white)
        QtWidgets.qApp.processEvents()
        QtWidgets.qApp.setPalette(lightMode)


class dirSelectWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.left = 600
        self.top = 400
        self.width = 640
        self.height = 480
        self.settings = Settings()
        self.settings.settings
        self.setupUI()

    def setupUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog(title="Lesson Plans", repo='lessonPlans')
        self.openFileNameDialog(title="Class Repo", repo='classRepo')
        daySelect()

    def openFileNameDialog(self, title=str, repo=str):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dirName = QtWidgets.QFileDialog.getExistingDirectory(
            self, f'Select {title}', options=options)
        if dirName:
            self.settings.write(repo, '~/' + Path(
                dirName).relative_to(Path().home()).as_posix())
        if repo == 'classRepo':
            self.class_path = Path(dirName).expanduser()


class daySelect(QtWidgets.QDialog):
    def __init__(self):
        super(daySelect, self).__init__()
        self.ui = Dialog()
        self.ui.setupUi(self)
        self.settings = Settings()
        self.class_repo = self.settings.class_path
        repo_children = [str(x.name)
                         for x in self.class_repo.expanduser().iterdir()]
        for item in repo_children:
            self.ui.daySelect.addItem(item)

        self.ui.fullTime.setDisabled(True)

        self.ui.buttonBox.clicked.connect(self.onSelect)
        self.exec_()

    def onSelect(self):
        self.settings.write('classDay', self.ui.daySelect.currentText())


if __name__ == "__main__":
    myappid = u'Class Helper'
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app_icon = QIcon()
    app_icon.addFile('img/toolbox.png', QSize(32, 32))
    app.setWindowIcon(app_icon)
    if not Path('settings.cfg').exists():
        dirSelectWindow()

    win = Window()

    sys.exit(app.exec())
