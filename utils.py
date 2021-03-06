from PyQt5 import QtCore, QtGui, QtWidgets
from pathlib import Path, PurePosixPath
from shutil import copytree, ignore_patterns
import json
import subprocess
import git
from git import Repo


# import threading
# from concurrent.futures import ProcessPoolExecutor, as_completed


class Settings:
    '''
    default(), write(parameter=str, value=str), dir_find(path=str, glob=str) threader()\n
    Handles various settings functions including passing values as properties to other functions.

    '''

    def __init__(self):
        self.settings_path = Path('settings.cfg').expanduser()
        if self.settings_path.exists():
            self.load_settings()
        else:
            self.default()

    def load_settings(self):
        self.settings = json.load(self.settings_path.open())
        self.lesson_path = Path(self.settings['lessonPlans'])
        self.class_path = Path(self.settings['classRepo'])
        self.class_day = self.settings['classDay']
        self.theme = self.settings['theme']
        self.push_style = self.settings['pushStyle']
        self.commit_msg = self.settings['commitMsg']

    def default(self):
        '''Runs search downstream of '~' for pattern matching lesson plans and class repos.'''
        # paths = self.threader()

        self.settings_path.touch()

        default_set = {
            'lessonPlans': 'None',
            'classRepo': 'None',
            'classDay': 'None',
            'theme': 'light',
            'pushStyle': 'One Activity',
            'commitMsg': '00 - Solved'
        }
        self.settings_path.write_text(json.dumps(default_set))
        self.load_settings()

    def write(self, parameter=str, value=str):
        '''writes new value to settings object and dumps (saves values) to settings.json'''
        self.settings[parameter] = value
        self.settings_path.write_text(json.dumps(self.settings))


'''
    # This Section is for the search function, replaced by the directory selector windows but still cool =)

    def dir_find(self, path, glob):
        dir_list = Path(path).rglob('*/' + glob)
        return [x for x in dir_list]

    def threader(self):
        with ProcessPoolExecutor() as executor:
            master_threads = []
            class_threads = []
            masks = ['Photos', 'AppData', 'Pictures', 'Videos', 'Music',
                     'Contacts', 'Calendar', 'Searches', '3D Objects', 'bin', 'config', 'Cookies', 'Start Menu', 'Recent']
            starts = ['.', '_', 'ntuser', 'NTUSER']
            for path in Path().home().iterdir():
                if not any(path.name == mask for mask in masks) or not any(path.name.startswith(start) for start in starts) or not path.is_symlink():
                    class_threads.append(executor.submit(
                        self.dir_find, str(path), "*Attendance Policy*.pdf"))
                    master_threads.append(executor.submit(
                        self.dir_find, str(path), "*1-Lesson-Plans"))
            futures = zip(as_completed(master_threads),
                          as_completed(class_threads))
            for master_future, class_future in futures:
                if len([x for x in master_future.result()]) > 0:
                    try:
                        master_class = {"lessonPlans": {str(x.parent.name): '~/' + str(
                            x.parent.relative_to(Path().home()).as_posix()) for x in master_future.result()},
                            "classRepos": {str(x.parent.parent.name): '~/' + str(
                                x.parent.parent.relative_to(Path().home()).as_posix()) for x in class_future.result()}}
                        return master_class
                    except Exception as e:
                        print(f"{e} raised")
'''


class Setup:
    '''Copies lesson from lesson plans to class repo, sets up weekly gitignore and activity commit/push'''

    def __init__(self, lesson=str):
        self.settings = Settings()
        self.settings.load_settings()
        self.lesson = lesson

        self.full_lesson = self.settings.lesson_path / '01-Lesson-Plans' / self.lesson
        self.full_class = self.settings.class_path / \
            self.settings.class_day / self.lesson
        # Save yourself
        self.ignore = ignore_patterns('TimeTracker*', 'LessonPlan.md',
                                      'VideoGuide.md', '*eslintrc.json')
        self.ignore_path = Path(self.full_class, '.gitignore').expanduser()

    def saveyourself(self):
        '''Removes lesson level README.md as it contains homework walkthrough'''
        try:
            top_readme = self.settings.class_path / self.lesson / 'README.md'
            top_readme.expanduser().unlink()
        except FileNotFoundError:
            pass

    def copy(self):
        try:
            copytree(self.full_lesson.expanduser().as_posix(),
                     self.full_class.expanduser().as_posix(), ignore=self.ignore)
            self.saveyourself()
            self.init_ignore()
        except FileExistsError:
            print(
                f"{self.lesson} already exists in {str(self.settings.class_path.expanduser())}")
            pass

    def homework(self):
        lp_homework = self.settings.lesson_path / \
            '02-Homework' / self.lesson / 'Instructions'
        cl_homework = self.settings.class_path / 'Homework' / self.lesson
        hw_ignore = ignore_patterns('Solutions', '*eslintrc.json')

        try:
            copytree(lp_homework.expanduser().as_posix(),
                     cl_homework.expanduser().as_posix(), ignore=hw_ignore)
        except FileExistsError:
            print(f"{self.lesson} Homework already exists")

    def init_ignore(self):
        self.ignore_path.touch()
        solved = self.full_class.expanduser().glob('**/Solved')
        all_act = self.full_class.expanduser().glob('**/*solved')
        day = '1'
        with self.ignore_path.open(mode='w', encoding='utf-8', newline='\n') as ignore:
            ignore.write('# Class 1\n')
            if self.settings.push_style == 'All Unsolved':
                for line in solved:
                    activity = line.relative_to(
                        self.full_class.expanduser())
                    ignore.write('\n')
                    if not str(activity).startswith(day):
                        day = str(activity.as_posix()).split("/")[0]
                        ignore.write(f'\n# Class {day}\n\n')
                    ignore.write(activity.as_posix())
            else:
                for line in all_act:
                    activity = line.relative_to(
                        self.full_class.expanduser())
                    ignore.write('\n')
                    if not str(activity).startswith(day):
                        day = str(activity.as_posix()).split("/")[0]
                        ignore.write(f'\n# Class {day}\n\n')
                    ignore.write(activity.as_posix())

    def ignore_act(self, day=str, activity=str):
        '''
        Ignore individual activities
        '''
        with open(self.ignore_path.as_posix(), 'r') as ignore:
            ignore_lines = ignore.readlines()
        for line in range(len(ignore_lines)):
            if '#' not in ignore_lines[line]:
                if 'solved' in ignore_lines[line] and activity in ignore_lines[line]:
                    ignore_lines[line] = "# " + ignore_lines[line]
                    # print(f"Ignoring: {ignore_lines[line]}")
                    try:
                        if self.settings.push_style == 'One Activity' and 'Unsolved' in ignore_lines[line + 3]:
                            ignore_lines[line + 3] = "# " + \
                                ignore_lines[line + 3]
                    except IndexError:
                        print('IndexError')
                        pass
        with open(self.ignore_path.as_posix(), 'w') as ignore:
            ignore.writelines(ignore_lines)
        self.push_act(activity)

    def push_act(self, activity=str):
        var_name = ' '
        print(self.settings.commit_msg)
        print(type(self.settings.commit_msg))
        if self.settings.commit_msg == "00-Lesson_name - Solved":
            self.commit_msg = activity + " - Solved"
            print("1")

        elif self.settings.commit_msg == "Lesson_name - Solved":
            split = activity.split('-')[1].split('_')
            self.commit_msg = var_name.join(split) + " - Solved"
            print("2")
        elif self.settings.commit_msg == "00 - Solved":
            split = activity.split('-')[0].split('_')
            self.commit_msg = var_name.join(split) + " - Solved"
            print("3")
        repo = Repo(self.settings.class_path.expanduser())
        git = repo.git
        ssh_cmd = 'ssh -i id_rsa'
        with git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            # print(f"Commit Message: {self.commit_msg}")
            # git.pull()
            # git.add('-A')
            # git.commit('-m', commit_msg)
            # git.push('origin', 'master')
            ''' @Todo: tie logger into data text for Window()'''


class Ui_MainWindow(object):
    '''UI settings for the main application window'''

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 325)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(640, 325))
        MainWindow.setMaximumSize(QtCore.QSize(640, 325))
        font = QtGui.QFont()
        font.setFamily("Hack")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.addLesson = QtWidgets.QPushButton(self.centralwidget)
        self.addLesson.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.addLesson.sizePolicy().hasHeightForWidth())
        self.addLesson.setSizePolicy(sizePolicy)
        self.addLesson.setMinimumSize(QtCore.QSize(0, 0))
        self.addLesson.setObjectName("addLesson")
        self.gridLayout.addWidget(self.addLesson, 10, 10, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 2, 1)
        self.activitiesDone = QtWidgets.QListView(self.centralwidget)
        self.activitiesDone.setObjectName("activitiesDone")
        self.gridLayout.addWidget(self.activitiesDone, 1, 8, 8, 4)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 7, 12, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 8, 1, 4)
        self.lessonProgress = QtWidgets.QProgressBar(self.centralwidget)
        self.lessonProgress.setProperty("value", 0)
        self.lessonProgress.setObjectName("lessonProgress")
        self.gridLayout.addWidget(self.lessonProgress, 10, 0, 1, 9)
        self.activityList = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.activityList.sizePolicy().hasHeightForWidth())
        self.activityList.setSizePolicy(sizePolicy)
        self.activityList.setMinimumSize(QtCore.QSize(275, 30))
        self.activityList.setMaximumSize(QtCore.QSize(600, 30))
        self.activityList.setObjectName("activityList")
        self.gridLayout.addWidget(self.activityList, 6, 0, 1, 1)
        self.pushActivity = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushActivity.sizePolicy().hasHeightForWidth())
        self.pushActivity.setSizePolicy(sizePolicy)
        self.pushActivity.setObjectName("pushActivity")
        self.gridLayout.addWidget(self.pushActivity, 10, 11, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 10, 9, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 10, 12, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 9, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 5, 6, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_2.setObjectName("radioButton_2")
        self.buttonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radioButton_2)
        self.gridLayout.addWidget(self.radioButton_2, 4, 4, 1, 1)
        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setObjectName("radioButton")
        self.buttonGroup.addButton(self.radioButton)
        self.gridLayout.addWidget(self.radioButton, 4, 3, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 4, 6, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.gridLayout.addItem(spacerItem6, 7, 0, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem7, 10, 13, 1, 1)
        self.radioButton_3 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_3.setObjectName("radioButton_3")
        self.buttonGroup.addButton(self.radioButton_3)
        self.gridLayout.addWidget(self.radioButton_3, 4, 5, 1, 1)
        self.lessonList = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lessonList.sizePolicy().hasHeightForWidth())
        self.lessonList.setSizePolicy(sizePolicy)
        self.lessonList.setMinimumSize(QtCore.QSize(250, 30))
        self.lessonList.setMaximumSize(QtCore.QSize(600, 30))
        self.lessonList.setObjectName("lessonList")
        self.gridLayout.addWidget(self.lessonList, 4, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Settings = QtWidgets.QMenu(self.menubar)
        self.menu_Settings.setObjectName("menu_Settings")
        self.menu_Weekly_Setup_Format = QtWidgets.QMenu(self.menu_Settings)
        self.setup_group = QtWidgets.QActionGroup(
            self.menu_Weekly_Setup_Format)
        self.menu_Weekly_Setup_Format.setGeometry(
            QtCore.QRect(1134, 195, 135, 94))
        self.menu_Weekly_Setup_Format.setObjectName(
            "menu_Weekly_Setup_Format")
        self.menu_Commit_Msg = QtWidgets.QMenu(self.menu_Settings)
        self.menu_Commit_Msg.setObjectName("menu_Commit_Msg")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Set_Lesson_Plans = QtWidgets.QAction(MainWindow)
        self.action_Set_Lesson_Plans.setCheckable(False)
        self.action_Set_Lesson_Plans.setObjectName(
            "action_Set_Lesson_Plans")
        self.action_Set_Class_Repo = QtWidgets.QAction(MainWindow)
        self.action_Set_Class_Repo.setCheckable(True)
        self.action_Set_Class_Repo.setObjectName("action_Set_Class_Repo")
        self.action_Dark_Mode = QtWidgets.QAction(MainWindow)
        self.action_Dark_Mode.setCheckable(True)
        self.action_Dark_Mode.setObjectName("action_Dark_Mode")
        self.actionOne_Activity = QtWidgets.QAction(MainWindow)
        self.actionOne_Activity.setCheckable(True)
        self.actionOne_Activity.setObjectName("actionOne_Activity")
        self.actionAll_Unsolved = QtWidgets.QAction(MainWindow)
        self.actionAll_Unsolved.setCheckable(True)
        self.actionAll_Unsolved.setObjectName("actionAll_Unsolved")
        self.actionLesson_Name_Solved = QtWidgets.QAction(MainWindow)
        self.actionLesson_Name_Solved.setCheckable(True)
        self.actionLesson_Name_Solved.setObjectName(
            "actionLesson_Name_Solved")
        self.action00_Solved = QtWidgets.QAction(MainWindow)
        self.action00_Solved.setCheckable(True)
        self.action00_Solved.setObjectName("action00_Solved")
        self.action00_Lesson_name_Solved = QtWidgets.QAction(MainWindow)
        self.action00_Lesson_name_Solved.setCheckable(True)
        self.action00_Lesson_name_Solved.setObjectName(
            "action00_Lesson_name_Solved")
        self.menu_File.addAction(self.action_Set_Lesson_Plans)
        self.menu_Weekly_Setup_Format.addAction(self.actionOne_Activity)
        self.menu_Weekly_Setup_Format.addAction(self.actionAll_Unsolved)
        self.setup_group.addAction(self.actionOne_Activity)
        self.setup_group.addAction(self.actionAll_Unsolved)
        self.setup_group.setExclusive(True)
        self.commit_group = QtWidgets.QActionGroup(self.menu_Commit_Msg)
        self.commit_group.setExclusive(True)
        self.menu_Commit_Msg.addAction(self.actionLesson_Name_Solved)
        self.menu_Commit_Msg.addAction(self.action00_Solved)
        self.menu_Commit_Msg.addAction(self.action00_Lesson_name_Solved)
        self.commit_group.addAction(self.actionLesson_Name_Solved)
        self.commit_group.addAction(self.action00_Solved)
        self.commit_group.addAction(self.action00_Lesson_name_Solved)
        self.menu_Settings.addAction(
            self.menu_Weekly_Setup_Format.menuAction())
        self.menu_Settings.addAction(self.menu_Commit_Msg.menuAction())
        self.menu_Settings.addSeparator()
        self.menu_Settings.addAction(self.action_Dark_Mode)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Settings.menuAction())

        self.retranslateUi(MainWindow)
        self.pushActivity.clicked.connect(self.activitiesDone.update)
        self.pushActivity.clicked.connect(self.lessonProgress.update)
        self.pushActivity.clicked.connect(self.activityList.update)
        self.lessonList.currentIndexChanged['int'].connect(
            self.activityList.update)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "TA Toolbox - Class Helper"))
        self.addLesson.setText(_translate("MainWindow", "Add Lesson"))
        self.label_2.setText(_translate("MainWindow", "Lesson:"))
        self.label_5.setText(_translate("MainWindow", "Day:"))
        self.label_3.setText(_translate("MainWindow", "Pushed Activities:"))
        self.pushActivity.setText(_translate("MainWindow", "Push Activity"))
        self.label_4.setText(_translate("MainWindow", "Lesson Progress:"))
        self.label.setText(_translate("MainWindow", "Activity:"))
        self.radioButton_2.setText(_translate("MainWindow", "2"))
        self.radioButton.setText(_translate("MainWindow", "1"))
        self.radioButton_3.setText(_translate("MainWindow", "3"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Settings.setTitle(_translate("MainWindow", "&Settings"))
        self.menu_Weekly_Setup_Format.setTitle(
            _translate("MainWindow", "&Push Style"))
        self.menu_Commit_Msg.setTitle(_translate("MainWindow", "&Commit Msg"))
        self.action_Set_Lesson_Plans.setText(
            _translate("MainWindow", "Set Directories"))
        self.action_Set_Lesson_Plans.setStatusTip(
            _translate("MainWindow", "Set new root directories"))
        self.action_Set_Class_Repo.setText(
            _translate("MainWindow", "Set Class Repo"))
        self.action_Set_Class_Repo.setStatusTip(_translate(
            "MainWindow", "Set a location for the class repository"))
        self.action_Dark_Mode.setText(_translate("MainWindow", "&Dark Mode"))
        self.actionOne_Activity.setText(
            _translate("MainWindow", "One Activity"))
        self.actionAll_Unsolved.setText(
            _translate("MainWindow", "All Unsolved"))
        self.actionLesson_Name_Solved.setText(
            _translate("MainWindow", "Lesson_Name - Solved"))
        self.action00_Solved.setText(_translate("MainWindow", "00 - Solved"))
        self.action00_Lesson_name_Solved.setText(
            _translate("MainWindow", "00-Lesson_name - Solved"))


class Dialog(object):
    '''UI settings for the class day select window'''

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(430, 110)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Hack")
        Dialog.setFont(font)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 70, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.fullTime = QtWidgets.QPushButton(Dialog)
        self.fullTime.setGeometry(QtCore.QRect(20, 75, 75, 23))
        self.fullTime.setObjectName("fullTime")
        self.daySelect = QtWidgets.QComboBox(Dialog)
        self.daySelect.setGeometry(QtCore.QRect(20, 30, 381, 22))
        self.daySelect.setObjectName("daySelect")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select Class Day"))
        self.fullTime.setText(_translate("Dialog", "One Class"))
