# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Mikhail Mehanig](https://github.com/mehanig/stepic_server_django).

## [Unreleased][unreleased]
###

## [0.1.1] - 2015-07-16
### Added
- Automatically merge 2 videos in one (left and right)
- .is_locked for substep added
- Blocking for deletion added
- Instance title added to submit deletion dialog
- Wrong username and password added

### Changed
- Default name for substep is user-customizable, default template for displaying is SubStep1from111 (was Step1from111)
- Substep template is customizable at /settings page and accept template variables: $id and $stepid
- New message at recording screen: "..Press here to stop."
- Sorting substeps by creation time

### Fixed
- Unable to delete lesson. views.delete_lesson signature changed.


## [0.1.0] - 2015-07-02
### Changed
- Changelog Started