""" ESC/POS configuration manager.

This module contains the implentations of abstract base class :py:class:`Config`.

"""

from __future__ import absolute_import

import os
import appdirs
import yaml

from . import printer
from . import exceptions

class Config(object):
    """  Configuration handler class.

    This class loads configuration from a default or specificed directory. It
    can create your defined printer and return it to you.
    """
    _app_name = 'python-escpos'
    _config_file = 'config.yaml'

    def __init__(self):
        self._has_loaded = False
        self._printer = None

        self._printer_name = None
        self._printer_config = None

    def load(self, config_path=None):
        """ Load and parse the configuration file using pyyaml

        :param config_path: An optional file path, file handle, or byte string
            for the configuration file.

        """
        if not config_path:
            config_path = os.path.join(
                appdirs.user_config_dir(self._app_name),
                self._config_file
            )

        try:
            if isinstance(config_path, file):
                config = yaml.safe_load(config_path)
            else:
                with open(config_path, 'rb') as f:
                    config = yaml.safe_load(f)
        except EnvironmentError:
            raise exceptions.ConfigNotFoundError('Couldn\'t read config at {config_path}'.format(
                config_path=str(config_path),
            ))
        except yaml.YAMLError as e:
            raise exceptions.ConfigSyntaxError('Error parsing YAML')

        if 'printer' in config:
            self._printer_config = config['printer']
            self._printer_name = self._printer_config.pop('type').title()

            if not self._printer_name or not hasattr(printer, self._printer_name):
                raise exceptions.ConfigSyntaxError('Printer type "{printer_name}" is invalid'.format(
                    printer_name=self._printer_name,
                ))

        self._has_loaded = True

    def printer(self):
        """ Returns a printer that was defined in the config, or None.

        This method loads the default config if one hasn't beeen already loaded.

        """
        if not self._has_loaded:
            self.load()

        if not self._printer:
            # We could catch init errors and make them a ConfigSyntaxError, 
            # but I'll just let them pass
            self._printer = getattr(printer, self._printer_name)(**self._printer_config)

        return self._printer

