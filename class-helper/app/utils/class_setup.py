from pathlib import Path
from shutil import copytree, ignore_patterns
import json
from .settings import Settings
import subprocess


class Setup:
    def __init__(self, lesson):
        self.settings = Settings()
        self.lesson = lesson
        # Save yourself
        self.ignore = ignore_patterns('TimeTracker*', 'LessonPlan.md',
                                      'VideoGuide.md', '*eslintrc.json')

    def saveyourself(self):
        try:
            top_readme = self.settings.class_path / self.lesson / 'README.md'
            top_readme.expanduser().unlink()
        except FileNotFoundError:
            pass

    def copy(self):
        full_lesson = self.settings.lesson_path / '01-Lesson-Plans' / self.lesson
        self.full_class = self.settings.class_path / \
            self.settings.class_day / self.lesson
        try:
            copytree(full_lesson.expanduser().as_posix(),
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
        ignore_path = Path(self.full_class, '.gitignore').expanduser()
        ignore_path.touch()
        solved = self.full_class.expanduser().glob('**/Solved')
        all_act = self.full_class.expanduser().glob('**/*solved')
        day = '1'
        with ignore_path.open(mode='w', encoding='utf-8', newline='\n') as ignore:
            ignore.write('# Class 1\n')
            if self.settings.push_style == 'All Unsolved':
                for line in solved:
                    activity = line.relative_to(
                        self.full_class.expanduser())
                    ignore.write('\n')
                    if str(activity).startswith(day):
                        pass
                    else:
                        day = str(activity.as_posix()).split("/")[0]
                        ignore.write(f'\n# Class {day}\n\n')
                    ignore.write(activity.as_posix())
            else:
                for line in all_act:
                    activity = line.relative_to(
                        self.full_class.expanduser())
                    ignore.write('\n')
                    if str(activity).startswith(day):
                        pass
                    else:
                        day = str(activity.as_posix()).split("/")[0]
                        ignore.write(f'\n# Class {day}\n\n')
                    ignore.write(activity.as_posix())
        print(ignore_path.expanduser().read_text())
