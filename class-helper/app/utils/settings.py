import json
from pathlib import Path, PurePosixPath
# import threading
# from concurrent.futures import ProcessPoolExecutor, as_completed


class Settings:
    '''
    default(), write(parameter=str, value=str), dir_find(path=str, glob=str) threader()\n
    Handles various settings functions including passing values as properties to other functions.

    '''

    def __init__(self):
        self.settings_path = Path('./class-helper/settings.json').expanduser()
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

    def write(self, parameter, value):
        '''writes new value to settings object and dumps (saves values) to settings.json'''
        self.settings[parameter] = value
        self.settings_path.write_text(json.dumps(self.settings))

    # def dir_find(self, path, glob):
    #     ''' Sets up recursive glob search downstream of `path` with mask glob.'''
    #     dir_list = Path(path).rglob('*/' + glob)
    #     return [x for x in dir_list]

    # def threader(self):
    #     '''Splits downstream dirs into separate processes each running dir_find, filters common system/unlikely parent directories. Returns dictionary with all matches.'''
    #     with ProcessPoolExecutor() as executor:
    #         master_threads = []
    #         class_threads = []
    #         masks = ['Photos', 'AppData', 'Pictures', 'Videos', 'Music',
    #                  'Contacts', 'Calendar', 'Searches', '3D Objects', 'bin', 'config', 'Cookies', 'Start Menu', 'Recent']
    #         starts = ['.', '_', 'ntuser', 'NTUSER']
    #         for path in Path().home().iterdir():
    #             if any(path.name == mask for mask in masks) or any(path.name.startswith(start) for start in starts) or path.is_symlink():
    #                 pass
    #             else:
    #                 class_threads.append(executor.submit(
    #                     self.dir_find, str(path), "*Attendance Policy*.pdf"))
    #                 master_threads.append(executor.submit(
    #                     self.dir_find, str(path), "*1-Lesson-Plans"))
    #         futures = zip(as_completed(master_threads),
    #                       as_completed(class_threads))
    #         for master_future, class_future in futures:
    #             if len([x for x in master_future.result()]) > 0:
    #                 try:
    #                     master_class = {"lessonPlans": {str(x.parent.name): '~/' + str(
    #                         x.parent.relative_to(Path().home()).as_posix()) for x in master_future.result()},
    #                         "classRepos": {str(x.parent.parent.name): '~/' + str(
    #                             x.parent.parent.relative_to(Path().home()).as_posix()) for x in class_future.result()}}
    #                     return master_class
    #                 except Exception as e:
    #                     print(f"{e} raised")
