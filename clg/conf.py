# coding: utf-8

import os
import sys
import clg
import yaml
import yamlordereddictloader
from addict import Dict
from collections import OrderedDict


class CLGConfigError(Exception):
    def __init__(self, filepath, msg):
        Exception.__init__(self, msg)
        self.filepath = filepath
        self.msg = msg

    def __str__(self):
        return '(%s) %s' % (self.filepath, self.msg)


def replace_paths(value):
    """Replace *__FILE__* string in ``value`` (if it is not a string, recursively
    parse the data) by the path of the main script (``sys.path[0]``).
    """
    return {
        str: lambda: value.replace('__FILE__', sys.path[0]),
        list: lambda: [replace_paths(elt) for elt in value],
        dict: lambda: {key: replace_paths(val) for key, val in value.items()},
        OrderedDict: lambda: {key: replace_paths(val) for key, val in value.items()}
    }.get(type(value), lambda: value)()


class Config(OrderedDict):
    def init(self, args):
        """Initialize the object with command-line arguments ``args``."""
        conf_file = os.path.expanduser(
            args['conf_file'] or os.path.join(sys.path[0], 'conf.yml'))
        conf_dir = os.path.expanduser(
            args['conf_dir'] or os.path.join(os.path.dirname(conf_file), 'conf'))
        commands = [value for (arg, value) in sorted(args) if arg.startswith('command')]

        # Load main configuration file.
        if os.path.exists(conf_file):
            self.load_cmd_file(conf_file)

        # Load intermediary configuration files.
        if os.path.exists(conf_dir):
            self.load_dir(conf_dir, clg.config, commands)

    def __getattribute__(self, name):
        """Allow direct access to elements in uppercase."""
        if name.isupper():
            return self[name]
        else:
            return OrderedDict.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Allow elements in uppercase to be added to the OrderedDict."""
        if name.isupper():
            self[name] = value
        else:
            return OrderedDict.__setattr__(self, name, value)

    def load_cmd_file(self, filepath):
        """Load YAML file ``filepath`` and add each element to the object.."""
        try:
            conf = yaml.load(open(filepath), Loader=yamlordereddictloader.Loader)
        except (IOError, yaml.YAMLError) as err:
            raise CLGConfigError(filepath, 'unable to load file: %s' % err)

        for param, value in conf.items():
            setattr(self, param.upper(), replace_paths(value))

    def load_dir(self, dirpath, config, commands):
        """Recursively load ``dirpath`` directory for adding elements in the object
        based on the current configuration ``config`` and the current ``commands``.
        """
        def get_subcommands(config):
            return ({}
                    if not 'subparsers' in config
                    else config['subparsers'].get('parsers', config['subparsers']))

        config = get_subcommands(config)

        while commands:
            cur_command = commands.pop(0)

            # Load command's configuration file and directory.
            cmd_dirpath = os.path.join(dirpath, cur_command)
            cmd_filepath = '%s.yml' % cmd_dirpath
            if os.path.exists(cmd_filepath):
                self.load_cmd_file(cmd_filepath)
            if os.path.exists(cmd_dirpath):
                # Be sure directory is loaded for last commands (tree's leaves).
                self.load_dir(cmd_dirpath, config[cur_command], commands or [cur_command])

            # Load files and directories that are not for other subcommands.
            for filename in sorted(os.listdir(dirpath)):
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    filename, fileext = os.path.splitext(filename)
                    if filename not in config:
                        setattr(self, filename.upper(), self.load_file(filepath))
                elif filename not in config:
                    setattr(self, filename.upper(), self.load_subdir(filepath))

    def load_subdir(self, dirpath):
        """Recursively parse ``dirpath`` directory for retrieving all
        configuration elements.
        """
        conf = Dict()
        for filename in sorted(os.listdir(dirpath)):
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                conf[os.path.splitext(filename)[0]] = self.load_file(filepath)
            else:
                conf[filename] = self.load_subdir(filepath)
        return conf

    def load_file(self, filepath):
        """Load ``filepath`` file based on its extension."""
        _, fileext = os.path.splitext(filepath)
        with open(filepath) as fhandler:
            return replace_paths({
                '.yml': lambda: yaml.load(fhandler, Loader=yamlordereddictloader.Loader),
                '.json': lambda: json.load(fhandler, object_pairs_hook=OrderedDict)
            }.get(fileext, lambda: fhandler.read())())

    def pprint(self):
        """Pretty print the object using `json` module."""
        import json
        return json.dumps(OrderedDict(self.items()), indent=4)

sys.modules[__name__] = Config()
