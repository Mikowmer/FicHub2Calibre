from calibre.utils.config import JSONConfig

from calibre_plugins.FicHub2Calibre import FicHub2CalibreBase

from qt.core import QWidget, QHBoxLayout, QLabel, QLineEdit

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# to ensure you don't accidentally clobber a calibre config file
prefs = JSONConfig('plugins/interface_demo')

# Set defaults
prefs.defaults['hello_world_msg'] = 'Hello, World!'
prefs.defaults['User-Agent'] = "FicHub2Calibre/%d.%d.%d" % FicHub2CalibreBase.version


# TODO: Add settings to profile
class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.hboxlayout = QHBoxLayout()
        self.setLayout(self.hboxlayout)

        self.label = QLabel('Hello world &message:')
        self.hboxlayout.addWidget(self.label)

        self.msg = QLineEdit(self)
        self.msg.setText(prefs['hello_world_msg'])
        self.hboxlayout.addWidget(self.msg)
        self.label.setBuddy(self.msg)

    def save_settings(self):
        prefs['hello_world_msg'] = self.msg.text()
