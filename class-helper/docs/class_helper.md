# Documentation

## Setup

If you only have one class repo and one lesson-plans folder, the setup will be handled automatically the first time you run class-helper. Don't be alarmed if it takes a second, this is normal as it's finding the class directory and the master lesson plans by walking through your file system and searching for markers associated with each directory tree. When it finishes it will populate a settings file with the directories and load the ui.

If you have multiple class directories or lesson plans, it will automatically choose the first one alphabetically. I realize this isn't always ideal but I had to pick one so there you go.

## Using Class Helper

Once setup is complete and the UI is visible, you can choose a lesson (populated from the lesson plans) and a class day (1,2,3). This will populate the activities (also populated from the lesson plans) as well as the pushed lessons (populated from the class repo lesson-level gitignore).

**Note**: because it's populated from the lesson plans, there may (and should be) lessons that do not _yet_ exist in the class repo. If you click on those you will get an error message that let's you know that file path doesn't exist in the class repo.
