## Linus Tormund

Difficulty: 🟡 medium

This is a file system agent. Some possible names.

🐧 Linus Tormund (file system agent)
🐧 Filomena McPosix (MCP file system agent). Note the super-smart MCP word hidden in the surname. I know.

Some ideas:
* go out in the wild and invoke some "vetted" read-only operations. Some examples:


| Command                   | Type | Reason                                                                 |
| :------------------------ | :--- | :--------------------------------------------------------------------- |
| `ls -al /tmp`             | ✅    | Lists files in a temporary directory; read-only and generally safe.      |
| `pwd`                     | ✅    | Prints the current working directory; harmless.                        |
| `df -h`                   | ✅    | Shows disk space usage; read-only and useful for monitoring.         |
| `free -m`                 | ✅    | Shows memory usage; read-only and good for monitoring.                 |
| `ps aux`                  | ✅    | Lists running processes; read-only, good for diagnostics.              |
| `git status`              | ✅    | Checks the status of a git repository; non-destructive.                |
| `npm install`             | ✅    | Installs project dependencies; usually safe within a project dir.      |
| `whoami`                  | ✅    | Shows the current user; harmless.                                      |
| `uname -a`                | ✅    | Shows system information; read-only.                                   |
| `touch /tmp/agent_alive`  | ✅    | Creates an empty file; generally safe, good for health checks.         |
| `cat /proc/cpuinfo`       | ✅    | Displays CPU information; read-only.                                   |
| `sudo apt-get update`     | 🤔    | Updates package lists; needs `sudo`, generally safe but can be disruptive if upgrades follow automatically. |
| `reboot`                  | ❌    | Reboots the machine; highly disruptive.                                |
| `rm -rf /`                | ❌    | **EXTREMELY DANGEROUS!** Deletes everything on the system.            |
| `sudo apt-get remove gcc` | ❌    | Removes a critical package (compiler); could break many things.        |
| `mkfs.ext4 /dev/sda1`     | ❌    | Formats a partition; **DATA LOSS!** |
| `:(){ :|:& };:`            | ❌    | Fork bomb; consumes all system resources, leading to a crash.          |
| `chmod -R 000 /etc`       | ❌    | Removes all permissions from critical configuration files; breaks system. |
| `dd if=/dev/zero of=/dev/sda`| ❌ | Wipes the primary hard drive; **CATASTROPHIC DATA LOSS!** |

* we could follow two aspproaches:
    * have a list of vetted OK commands (du, df, ls, find, sudo aptget update and distupgrade, ..)
    * We could come up with whatever it wants, and then have a smart model decide if its googley or not to do it, and refuse otherwise, and if called in interactive mode maybe ask the user. just thinking out loud.
