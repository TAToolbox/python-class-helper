import json
from pathlib import Path, PurePosixPath
from threading import Thread


class Settings:
    def __init__(self):
        self.settings_path = Path('../../class-helper/settings.json')
        if self.settings_path.exists():
            self.settings = json.load(self.settings_path.open())
            self.lesson_path = Path(self.settings['lessonPath'])
            self.class_path = Path(self.settings['classPath'])
            self.class_day = self.settings['classDay']
            self.theme = self.settings['theme']
            self.push_style = self.settings['pushStyle']
            self.commit_msg = self.settings['commitMsg']
        else:
            self.default()

    def default(self):
        self.threader()

        self.settings_path.touch()

        default_set = {
            'lessonPath': str(PurePosixPath('~') / self.master_opt[0].relative_to(Path.home())),
            'classPath': str(PurePosixPath('~') / self.class_opt[0].relative_to(Path.home())),
            'classDay': str([x.name for x in Path(self.class_opt[0]).iterdir() if 'MW' in x.name][0]),
            'theme': 'light',
            'pushStyle': 'One Activity',
            'commitMsg': '00 - Solved'
        }
        self.settings_path.write_text(json.dumps(default_set))

    def write(self, parameter, value):
        self.settings[parameter] = value
        self.settings_path.write_text(json.dumps(self.settings))

    def findMaster(self):
        self.master_opt = [x.parent
                           for x in Path('~').expanduser().glob('**/*1-Lesson-Plans')]

    def findClass(self):
        self.class_opt = [x.parent.parent
                          for x in Path('~').expanduser().glob('**/*Attendance Policy*.pdf')]

    def threader(self):
        threads = []
        processes = [self.findClass, self.findMaster]
        for process in processes:
            thread = Thread(target=process)
            thread.start()
            threads.append(thread)
        for process in threads:
            process.join()
