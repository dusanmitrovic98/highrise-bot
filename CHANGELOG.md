<!-- TODO: Add details for the next release below. -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.26] - 2025-06-10
- Initial production test release.

## [0.0.25] - 2025-06-10
- Rollback release.
- Stable with radio tts package working under stable conditions.
- Radio tts needs improvements.

## [0.0.24] - 2025-06-07

### Removed
- The "ghost me" chat command and all related ghost loop logic from the bot.
- Unused asyncio import after feature removal.

## [0.0.24] - 2025-06-07

### Changed
- Refactored emote command: centralized the logic for stopping user emote loops into a single stop_emote_loop method, reducing code duplication and improving maintainability.

## [0.0.23] - 2025-06-07

### Added
- !emote details now supports both emote names and numbers (by index).

### Fixed
- If !emote details is called with an invalid name or number, it returns early and does not stop any running emote loop.
- Improved robustness for category handling in details and lookup logic.

## [0.0.22] - 2025-06-07
### Added
- Support for multiple categories per emote (comma-separated, stored as arrays).
- !emote list categories now displays categories in numbered blocks.

### Changed
- All emote category fields are now arrays for consistency and future flexibility.
- Listing emotes by category now works with multi-category emotes.

### Fixed
- Fixed JSONDecodeError on invalid emote data.
- Improved robustness of emote category handling.

## [0.0.21] - 2025-06-07

### Added
- Support for starting and stopping emote loops directly from chat (not just via !emote command)
- Users can type a number, emote name, or emote id with "loop" and optional "interval=" to start a looping emote on themselves
- Typing "stop" in chat cancels the user's emote loop

### Fixed
- Improved argument parsing for quoted values (e.g., description="Wave at someone.") in emote save/update commands

### Changed
- Unified emote loop tracking for both command and chat triggers

## [v0.0.20] - 2025-06-07
### Added
- The !react command now supports custom sequences of reactions (e.g., !react heart clap wink @user 3 interval=2).
- You can combine any pattern of supported reactions and repeat them for a specified count and interval.
- The command works for self, specific users, or all users in the room.

### Changed
- Improved argument parsing and error messages for the !react command.

## [v0.0.19] - 2025-06-07

### Added
- New AI-powered ask command (`ask.py`) that allows users to ask questions in chat or DMs and receive responses from the AI.
- Supports both public chat and direct messages, with improved error handling and user feedback.
- Command can be triggered by prefix or keywords ("seb", "sebastian").

## [v0.0.18] - 2025-06-07

### Changed
- Refactored message event handler logic for improved clarity and modularity.
- Renamed `modulate_last_message_and_user` to `handle_last_message_and_user`.
- Extracted helper functions for fetching messages, user info, and logging.
- Enhanced maintainability and readability of the message event workflow.

## [0.0.17] - 2025-06-06

### Added
- New `wardrobe` plugin: manage and list saved outfits for the bot.
  - `!wardrobe` and `!wardrobe open` both list all saved outfits.
  - `!wardrobe save <name>` saves the bot's current outfit under the given name.
  - `!wardrobe remove <name>` removes a saved outfit by name.

### Fixed
- Outfit saving now serializes all items using `attrs.asdict` to ensure JSON compatibility.

## [0.0.16] - 2025-06-06

### Changed
- Changed the !spawn command to save the position of the user who invoked the command as the spawn point in config.json, instead of saving the bot's position.

## [0.0.15] - 2025-06-06

### Added
- On user join, new users are now automatically added as 'guest' to both users.json and permissions.json for consistent user management.

### Changed
- Refactored join event logic for improved code clarity and maintainability.

## [0.0.14] - 2025-06-06

### Added
- All event methods in `main.py` now log all their arguments in detail, using the format `[EVENT] arg1=... arg2=...` for each method, for improved debugging and monitoring.

### Changed
- Replaced all print statements in `main.py` with logger calls, and added logger setup at the top of the file.
- Log message formats now match those from `echo.py` for all relevant events.
---

## [0.0.13] - 2025-06-06

### Changed
- The !line command no longer requires or accepts a direction argument. It now supports unlimited @mentions and an optional spacing parameter.
- !line now centers the stack between the first and last user, placing all users in a line with equal spacing, centered on the midpoint.
- Improved collision avoidance for all users except the first in both !line and !swap.
- The !swap command maintains robust multi-user support and circular swapping logic.
- General improvements to user lookup and error handling in both commands.

## [0.0.12] - 2025-06-06
### Added
- Unlimited user support for the !swap command: you can now mention any number of users, and all will be swapped in a circular fashion (caller included).
- All teleports are now performed in parallel for faster and smoother swaps.

### Changed
- Improved swap logic to use temp values and avoid position overwrites.
- Maintains collision avoidance by offsetting z-coordinate during teleportation.

## [v0.0.11] - 2025-06-06

### Added
- Automatic registration of package ports in `runtime/ports/register.json` using port values from `plugins.json` or `commands.json`.
- `get_package_port` and `register_package_port` methods in `CommandHandler` for unified port lookup and registration.
- On package process start, the port is now always registered automatically.

### Changed
- Shutdown, reboot, and crash commands now:v0.
  - Kill only valid, nonzero PIDs (skip PID 0) when cleaning up port-bound processes.
  - Clean up the port registry only for ports that are no longer in use.
  - Handle empty or invalid `register.json` gracefully to prevent startup errors.

### Fixed
- Prevented repeated errors when attempting to kill PID 0 (system process) during shutdown.
- Ensured all package subprocesses and port-bound processes are reliably terminated on shutdown, reboot, or crash.

## [v0.0.10] - 2025-06-06

### Added
- All reaction commands (`!react`, `!clap`, `!heart`, `!thumbs`, `!wave`, `!wink`) now support an optional `[count]` and `[interval=seconds]` parameter.
  - Example: `!react heart @user1 @user2 3 interval=2` will send 3 heart reactions to each mentioned user, with 2 seconds between each.
  - Example: `!clap all 5 interval=1.5` will send 5 claps to every user in the room, with 1.5 seconds between each.
- The `interval=...` parameter can be placed anywhere in the command arguments.
- Usage help messages updated for all reaction commands.

---

## [0.0.9] - 2025-06-06

### Added
- `!entity save <name>`: Save the entity id you are currently anchored to under a custom name.
- `!entities`: List all saved entity names and ids.
- `!use <name|entity_id>`: Move the bot to the specified entity by name or id.

### Changed
- `!use` now resolves names from `config.json`'s entities section before falling back to raw ids.
- The entity plugin now creates the `entities` section in `config.json` automatically if it does not exist.

---

## [0.0.8] - 2025-06-06

### Added
- Default distance of 1 for `!push` and `!pull` commands if distance argument is not provided.

### Improved
- Error handling for missing user or position in push command.

---

## [0.0.7] - 2025-06-06

### Changed
- Refactor revoke command: use `!revoke role|permission @username name` pattern and update pattern matching.
- Improved clarity and consistency for permission/role revocation commands.

### Fixed
- Users are being added to `permission.json` on join.

---

## [0.0.6] - 2025-06-05

### Added
- Plugin/command event handler system: Commands can now register custom event handlers (e.g., on_chat) via CommandBase.
- Event dispatcher (chat) now calls all registered on_chat handlers for loaded commands/plugins.
- Plugin/command event handler system: Commands can now register custom event handlers (e.g., on_chat) via CommandBase.
- Event dispatcher (chat, join, etc.) now calls all registered handlers for loaded commands/plugins.
- Uses config-driven messages for thinking and error responses.

### Changed
- ask.py plugin updated to use the new handler system for chat-triggered AI responses.
- Streamlined ask plugin logic for clarity and maintainability.

### Fixed
- Fixed event handler system so that `bot.commands` is always populated with all loaded commands and plugins.
- Event-driven plugins (e.g., ask.py) now reliably receive events like chat, join, etc., even after reloads.
- on_chat handler no longer responds to direct command calls (e.g., !ask ...), preventing double responses.

### Notes
- This enables modular, event-driven plugin development for all future commands and plugins.

---

## [0.0.5] - 2025-06-05

### Added
- Added `!spawn` command: Owners can now set the bot's current position as the spawn point in `config.json` using the `!spawn` command. The command determines the bot's position by searching for its own user ID in the room and updates the spawn coordinates accordingly.
- Added blink plugin.
- Support for an optional "package" field in plugin configuration (plugins.json) to specify a package directory.
- Automatic management of package subprocesses: starts main.py for each package, and ensures only one instance runs at a time.
- On reload or bot start, any running package subprocess is terminated before starting a new one.

### Changed
- Updated bot spawn logic to use the `spawn` section from `config.json` instead of the deprecated `coordinates` key. The bot now correctly moves to the configured spawn position on reconnect.
- Improved `unstuck` command:
  - Teleports the caller to the bot spawn point if called with no mentions.
  - If one user is mentioned, uses the caller as the base location for unstucking.
  - If multiple users are mentioned, spreads them horizontally from the first mentioned user's position.
  - Uses spawn position and facing from config if available.
  - Provides clear feedback messages for all cases.
- Owner/admin users (with "*" permission) can now run any command, even if the command requires specific permissions.
- `!reload` command now reloads both commands and permissions, so changes to permissions.json are applied without restart.
- Removed all manual permission checks from command files; permission logic is now fully centralized.
- Fixed bot startup crash due to method order in CommandHandler.

### Fixed
- Fixed the `!spawn` command to use `get_room_users()` and `my_id` for determining the bot's position, ensuring compatibility with the current Highrise API.
- Fixed teleport command.
- All running plugin package subprocesses are now properly terminated on bot exit, crash, or kill (including Ctrl+C), preventing orphaned processes.

### Removed
- emote command

---

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

---

## [0.0.3] - 2025-06-03

### Added
- Added `/whoami` (aliases: `/myrole`, `/myperms`, `/permissions`) command: lets users see their user ID, username, and permissions.
- Added `/reload` (admin/owner only) command: allows hot-reloading of all commands and plugins at runtime without restarting the bot.
- Added `/whoami` (aliases: `/myrole`, `/myperms`, `/permissions`) command: lets users see their user ID, username, and permissions.
- Placeholder function `log_to_external_service(event_type, data)` in `handleCommands.py` for future external logging of command usage and errors (e.g., to a database or HTTP endpoint).

### Changed
- Improved error handling and user feedback for failed commands: users now receive more descriptive error messages, including permission and cooldown details.
- Enhanced logging: command usage and errors (with traceback and user context) are now logged for better diagnostics and analytics.

---

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

---

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