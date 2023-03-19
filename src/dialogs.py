#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__ = 'GPL v3'
__copyright__ = '2023, Mikowmer <@Mikowmer in FicHub Discord Server>'
__docformat__ = 'restructuredtext en'

from qt.core import QDialog, QVBoxLayout, QPushButton, QLabel, QFormLayout, QLineEdit, QDialogButtonBox, Qt

from calibre_plugins.FicHub2Calibre.config import prefs
from calibre.ebooks.metadata.meta import get_metadata

import requests
import json

from io import BytesIO

ficHubAPIAddress = 'https://fichub.net/api/v0/epub?q='


class FicHubDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)

        self.setWindowIcon(icon)

        self.gui = gui
        self.do_user_config = do_user_config

        # Setting up requests session:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': prefs['User-Agent']
        })

        try:
            self.db = gui.current_db.new_api
            print("Using New API")
        except AttributeError:
            self.db = gui.current_db
            print("Using Old API")

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        self.formLayout = QFormLayout()

        self.label = QLabel("Enter Fic &URL:", self)
        self.urlEntry = QLineEdit(self)
        self.urlEntry.setPlaceholderText("https://")

        self.formLayout.addRow(self.label, self.urlEntry)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.verticalLayout.addLayout(self.formLayout)

        self.ficDataOutput = QLabel("", self)
        self.verticalLayout.addWidget(self.ficDataOutput)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)

        self.ficDataButton = QPushButton('Get Fic Data', self)
        self.ficDataButton.clicked.connect(self.get_fic_data)
        self.buttonBox.addButton(self.ficDataButton, QDialogButtonBox.ActionRole)

        self.downloadButton = QPushButton('Download', self)
        self.downloadButton.clicked.connect(self.download)
        self.buttonBox.addButton(self.downloadButton, QDialogButtonBox.AcceptRole)

        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.close)

        self.verticalLayout.addWidget(self.buttonBox)

        self.resize(self.minimumSizeHint())

    def get_fic_data(self, button_clicked=True):
        if button_clicked:
            print("Get Fic Data Clicked")
        # TODO: Add spinner of some sort here in order to show activity prior to receiving response.
        # TODO: Make request asynchronous so that gui doesn't lock up.

        fic_url = self.urlEntry.text()

        # TODO: Add URL Sanity Check?

        queryURL = ficHubAPIAddress + fic_url

        # TODO: Add check for failed response
        response = self.session.get(queryURL)
        print(response)

        decoded_content = json.loads(response.content.decode("UTF-8"))
        print(decoded_content["info"])

        self.ficDataOutput.setText(decoded_content["info"])
        return decoded_content

    def download(self):
        print("Download Button Clicked")

        # TODO: Add check for failed response
        decoded_content = self.get_fic_data(button_clicked=False)
        ebook_url = decoded_content["epub_url"]
        print(ebook_url)

        # TODO: Add check for failed response
        ebook_blob = self.session.get("https://fichub.net" + ebook_url, allow_redirects=True, timeout=(6.1, 300))

        print("Download successful")

        ebook_blob_stream = BytesIO(ebook_blob.content)

        # TODO: Add try-except clauses to check for failed conversions
        id_, _ = self.db.add_books([(get_metadata(ebook_blob_stream, 'epub'), {'EPUB': ebook_blob_stream})])

        print("Download operations complete.")

        # Update Library Gui. Code "inspired" by DeDRM_tools/Obok_plugin/action.py/refresh_gui_lib
        self.gui.library_view.model().db.data.books_added(id_)
        self.gui.library_view.model().books_added(1)

        self.gui.db_images.reset()
        self.gui.tags_view.recount()
        self.gui.library_view.model().set_highlight_only(True)
        self.gui.library_view.select_rows(id_)
