# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HereGeocoder
                                 A QGIS plugin
 With this plugin you can geocode multiple adresses from JSON file, using HERE services with your API key
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-12
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Aldres
        email                : aldres98@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import *
from PyQt5.QtCore import *
from .geocode import *
from .geocoder_worker import GeocoderWorker

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .here_geocoder_dialog import HereGeocoderDialog
import os.path


class HereGeocoder:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.threadpool = QThreadPool()
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HereGeocoder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&HereGeocoder')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HereGeocoder', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/here_geocoder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'HereGeocoder'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&HereGeocoder'),
                action)
            self.iface.removeToolBarIcon(action)

    def create_point(self, layer):
        prov = layer.dataProvider()
        prov.addAttributes([QgsField("Address", QVariant.String)])
        layer.updateFields()
        point = QgsPointXY(address['Longitude'], address['Latitude'])
        feat = QgsFeature()
        # feat.setAttributes(address["AddressLabel"])
        feat.setAttributes([address["AddressLabel"]])
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        prov.addFeatures([feat])
        # layer.updateExtents()

    def select_input_file(self):
        filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select input file ", "", "*.json")
        self.dlg.FilePathField.setText(filename)
        self.fill_json_fields_box()

    def fill_json_fields_box(self):
        fields = get_json_fields_names(self.dlg.FilePathField.text())
        self.dlg.FieldsComboBox.clear()
        self.dlg.FieldsComboBox.addItems([field for field in fields])

    def geocode_from_file(self, addresses):
        worker = GeocoderWorker(addresses, KEY, self.layer)
        worker.progress.connect(self.update_progress)
        worker.start()
        self.threadpool.start(worker)


    def start_geocoding_thread(self, address):
        self.obj = GeocoderWorker(address, KEY, self.layer)  # no parent!
        self.thread = QThread()  # no parent!
        self.set_max_progress_value(len(address))
        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.progress.connect(self.update_progress)
        # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)
        # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)
        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.run)
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)
        # 6 - Start the thread
        self.thread.start()


    def set_max_progress_value(self, value):
        self.dlg.progressBar.setMaximum(value)


    def update_progress(self, progress):
        self.dlg.progressBar.setValue(progress)
        self.dlg.processEvents()

    def fill_layer_from_geocoded_data(self):
        api_key = self.dlg.ApiKeyField.text()
        addresses = gather_adresses_by_field(self.dlg.FilePathField.text(), str(self.dlg.FieldsComboBox.currentText()))
        self.start_geocoding_thread(addresses)
        # addresses = here(KEY, addresses)
        # for address in addresses:
        #     i = i + 1
        #     self.dlg.progressBar.setValue(i)
        #     prov = layer.dataProvider()
        #     prov.addAttributes([QgsField("Address", QVariant.String)])
        #     layer.updateFields()
        #     point = QgsPointXY(address['Longitude'], address['Latitude'])
        #     feat = QgsFeature()
        #     # feat.setAttributes(address["AddressLabel"])
        #     feat.setAttributes([address["AddressLabel"]])
        #     feat.setGeometry(QgsGeometry.fromPointXY(point))
        #     prov.addFeatures([feat])


    def run(self):
        """Run method that performs all the real work"""
        self.layer = QgsVectorLayer('Point?crs=epsg:4326', 'point', 'memory')
        QgsProject.instance().addMapLayers([self.layer])


        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            # self.layer = layer
            self.dlg = HereGeocoderDialog()
            self.dlg.pushButton.clicked.connect(self.select_input_file)
            self.dlg.geocode_button.clicked.connect(self.fill_layer_from_geocoded_data)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.thread.exit()
            pass
