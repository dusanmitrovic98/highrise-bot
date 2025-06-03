# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [0.0.3] - 2025-06-03

### Added
- Added `/whoami` (aliases: `/myrole`, `/myperms`, `/permissions`) command: lets users see their user ID, username, and permissions.

## [0.0.2] - 2025-06-03
### Added
- Added `reset` dev command: allows admins/owners to restart the bot process via chat command (`/reset` or `/restart`).

### Changed
- Refactored `CommandHandler` in `handleCommands.py` to add type annotations, improved error handling, and logging for command loading and execution.
- Improved command registration and permission handling for maintainability and robustness.
- Refactored `handleEvents.py` to use logging for error reporting instead of print, improving consistency and maintainability.
- Plugin loader: Commands can now be dynamically loaded from a `plugins/` directory for greater extensibility.

### Fixed
- Command loader now skips `command_base.py` and files without a `Command` class, preventing spurious log errors.
- Changed `/reset` command to exit the process, ensuring single restart when using monitor script.

## [0.0.1] - 2025-06-03

### Added
- CommandBase abstract class to standardize all command implementations.
- Refactored all command modules to inherit from the new `CommandBase` abstract class for consistency and maintainability.
- Fixed minor code issues and improved code structure in command modules.


# Format:

### Added
- Initial project setup.

### Changed

### Deprecated

### Removed

### Fixed

### Security