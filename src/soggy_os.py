"""
Module for SoggyOS, a simple Linux-like command line OS for the game.
"""
import re

class SoggyOS:
    """
    SoggyOS: A simple, command-line only, Linux-like OS for in-game computers.
    Handles command input, parsing, and output.
    """
    BLUE = (0, 128, 255)  # RGB for directories
    GREEN = (0, 255, 0)   # RGB for normal text

    def __init__(self):
        self.directories = {
            '/': ['home', 'bin', 'etc', 'tmp'],
            '/home': ['user'],
            '/home/user': [],
            '/bin': [],
            '/etc': [],
            '/tmp': []
        }
        self.files = {}  # Maps full file paths to file content (str)
        self.current_dir = '/home/user'
        self.username = 'soggy'
        self.hostname = 'computer'
        self.history = []  # Stores command history
        self.output = []   # Stores output lines (strings or special for ls)
        self._update_prompt()
        self._last_ls = None  # Store last ls output for rendering

    def _update_prompt(self):
        self.prompt = f'{self.username}@{self.hostname}:{self.current_dir}$ '

    def run_command(self, command):
        """
        Parse and execute a command string. Returns output as a string or dict (for editor mode).
        """
        self.history.append(command)
        tokens = command.strip().split()
        if not tokens:
            return ''
        cmd = tokens[0]
        args = tokens[1:]
        result = ''
        self._last_ls = None
        # Always add the prompt and command to output (except for clear)
        if cmd != 'clear':
            self.output.append(self.prompt + command)
        if cmd == 'help':
            result = 'Available commands: help, echo, clear, cd, ls, touch, edit'
        elif cmd == 'echo':
            result = ' '.join(args)
        elif cmd == 'clear':
            self.output.clear()
            result = ''
        elif cmd == 'cd':
            result = self._cd(args)
        elif cmd == 'ls':
            result = self._ls(args)
        elif cmd == 'touch':
            result = self._touch(args)
        elif cmd == 'edit':
            result = self._edit(args)
        else:
            result = f"Command not found: {command}"
        # Add whitespace before and after output
        if cmd == 'ls' and isinstance(result, list):
            self.output.append({'ls': result})
            self.output.append('')
            self._last_ls = result
        elif isinstance(result, str) and result:
            self.output.append(result)
            self.output.append('')
        # Do NOT append dicts (like editor) to output
        self._update_prompt()
        return result

    def _cd(self, args):
        if not args:
            self.current_dir = '/home/user'
            return ''
        path = args[0]
        # Handle '..' to go up one directory
        if path == '..':
            if self.current_dir == '/':
                return ''
            parent = '/'.join(self.current_dir.rstrip('/').split('/')[:-1])
            if not parent:
                parent = '/'
            self.current_dir = parent
            return ''
        # Handle absolute and relative paths
        if path.startswith('/'):
            target = path.rstrip('/') if path != '/' else '/'
        else:
            if self.current_dir == '/':
                target = '/' + path
            else:
                target = self.current_dir + '/' + path
        # Normalize path
        target = target.replace('//', '/')
        if target in self.directories:
            self.current_dir = target
            return ''
        else:
            return f"cd: no such file or directory: {path}"

    def _ls(self, args):
        """
        List contents of the current directory. Returns a list of (name, type) tuples, where type is 'dir' or 'file'.
        Files should be shown as white in the UI.
        """
        contents = self.directories.get(self.current_dir, [])
        # Add files in the current directory
        file_list = []
        for path, content in self.files.items():
            dir_path, file_name = path.rsplit('/', 1)
            if dir_path == self.current_dir:
                file_list.append((file_name, 'file'))
        dir_list = [(name, 'dir') for name in contents]
        return dir_list + file_list

    def _strip_ansi(self, text):
        # Remove ANSI escape codes for pygame rendering
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\033\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def get_prompt(self):
        return self.prompt

    def get_output(self):
        return self.output

    def get_last_ls(self):
        """Return the last ls output as a list of (name, type) tuples, or None."""
        return self._last_ls 

    def _touch(self, args):
        if not args:
            return 'touch: missing file operand'
        created = []
        for filename in args:
            if '/' in filename or filename in self.directories.get(self.current_dir, []):
                return f"touch: invalid file name: {filename}"
            path = self.current_dir.rstrip('/') + '/' + filename
            if path not in self.files:
                self.files[path] = ''
                created.append(filename)
        if created:
            return f"Created file(s): {' '.join(created)}"
        else:
            return ''

    def _edit(self, args):
        if not args:
            return 'edit: missing file operand'
        filename = args[0]
        if '/' in filename or filename in self.directories.get(self.current_dir, []):
            return f"edit: invalid file name: {filename}"
        path = self.current_dir.rstrip('/') + '/' + filename
        if path not in self.files:
            return f"edit: file not found: {filename}"
        # Signal to the UI to enter editor mode with this file
        return {'editor': {'path': path, 'content': self.files[path]}} 