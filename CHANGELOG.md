# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5] - 2025-06-04

### Added
- Added `!spawn` command: Owners can now set the bot's current position as the spawn point in `config.json` using the `!spawn` command. The command determines the bot's position by searching for its own user ID in the room and updates the spawn coordinates accordingly.
- Added blink plugin.

### Changed
- Updated bot spawn logic to use the `spawn` section from `config.json` instead of the deprecated `coordinates` key. The bot now correctly moves to the configured spawn position on reconnect.

### Fixed
- Fixed the `!spawn` command to use `get_room_users()` and `my_id` for determining the bot's position, ensuring compatibility with the current Highrise API.
- Fixed teleport command.

## [0.0.4] - 2025-06-03

### Added
- Defined roles (`owner`, `admin`, `moderator`, `user`, `guest`) and their default permissions in `permissions.json`.
- Established permissions system allowing users to have roles and custom/extra permissions.
- Added support for admins/owners to grant and revoke roles using `/grant_role @username role` and `/revoke_role @username role`.
- Updated `/grant_permission` to allow granting and revoking specific permissions as before.
- CommandBase now auto-loads command configuration (name, description, aliases, cooldown, permissions) from commands.json for all commands.
- Added `on_channel` event handler in `src/events/channel.py` to support hidden channel messages and admin/bot-to-bot communication.
- Enhanced `on_channel` to demonstrate usage: responds to 'admin' tag and handles a secret shutdown command via channel message.
- Added `before_start` event handler in `src/events/before_start.py` to support pre-startup logic and resource setup for the bot.

### Changed
- Updated permission system integration: `get_user_permissions` in `handleCommands.py` now supports roles and extra permissions from `permissions.json` and aggregates permissions accordingly.
- All core commands now use the new roles-based permission system from permissions.json. Deprecated static permissions in `config.py`.
- Refactored config system: config, loggers, messages, permissions, and authorization are now exported as dynamic classes backed by config.json, allowing persistent and editable configuration while maintaining backward compatibility with previous attribute access patterns.
- Removed redundant config loading from individual command classes.
- Updated `on_channel` event handler to demonstrate a real-life use case: handling a 'giveaway' tag to silently enter users into a giveaway and notify them via whisper, replacing the previous shutdown example.

### Fixed
- Fixed permission checks for owner users: commands now recognize 'owner' role as super admin and allow all actions as intended.
- Fixed permission checks to allow command execution if user has any required permission (not all), ensuring correct access for admin/owner roles.
- Fixed punctuation set syntax in remove_chars_until_punctuation to prevent syntax errors and improve response trimming.
- Fixed bot now always respects the follow distance set in config or via command, even if set as a string.

## [0.0.3] - 2025-06-03

### Added
- Added `/whoami` (aliases: `/myrole`, `/myperms`, `/permissions`) command: lets users see their user ID, username, and permissions.
- Added `/reload` (admin/owner only) command: allows hot-reloading of all commands and plugins at runtime without restarting the bot.
- Added `/whoami` (aliases: `/myrole`, `/myperms`, `/permissions`) command: lets users see their user ID, username, and permissions.
- Placeholder function `log_to_external_service(event_type, data)` in `handleCommands.py` for future external logging of command usage and errors (e.g., to a database or HTTP endpoint).

### Changed
- Improved error handling and user feedback for failed commands: users now receive more descriptive error messages, including permission and cooldown details.
- Enhanced logging: command usage and errors (with traceback and user context) are now logged for better diagnostics and analytics.

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