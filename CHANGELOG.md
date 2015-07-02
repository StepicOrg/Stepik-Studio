# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Mikhail Mehanig](https://github.com/mehanig/stepic_server_django).

## [Unreleased][unreleased]
### Added
- Automatically merge 2 videos in one (left and right), but no link added for downloading this file yet

### Changed
- Default name for substep is user-customizable, default template for displaying is SubStep1from111 (was Step1from111)
- Substep template is customizable at /settings page and accept template variables: $id and $stepid

### Fixed
- Unable to delete lesson. views.delete_lesson signature changed.


## [0.1.0] - 2015-07-02
### Changed
- Changelog Started