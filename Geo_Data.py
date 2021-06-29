# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoData
                                 A QGIS plugin
 This plugin gathers cz/sk data sources.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-04
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Test
        email                : test
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu, QMessageBox, QDialog
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu, QMessageBox, QDialog

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Geo_Data_dialog import GeoDataDialog
from .Region_dialog import RegionDialog
import os.path

from .crs_trans.RegionHandler import RegionHandler

class GeoData:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoData_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoData')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.toolbar = self.iface.addToolBar(u'GeoDataCZSK')
        self.toolbar.setObjectName(u'GeoDataCZSK')

        self.region_handler = RegionHandler(iface)

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
        return QCoreApplication.translate('GeoData', message)


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
#             self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(
            os.path.dirname(__file__), 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Browse data sources'),
            callback=self.run,
            parent=self.iface.mainWindow())

        icon_path = os.path.join(
                    os.path.dirname(__file__), 'icons/settings.png')
        self.add_action(
                    icon_path,
                    text=self.tr(u'Set region'),
                    callback=self.showSettings,
                    parent=self.iface.mainWindow())

        icon_path = os.path.join(
                            os.path.dirname(__file__), 'icons/save_to_project.png')
        self.add_action(
                    icon_path,
                    text=self.tr(u'Save settings to project'),
                    callback=self.saveRegionSettingsToProject,
                    parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoData'),
                action)
#             self.iface.removeToolBarIcon(action)
        del self.toolbar

    def saveRegionSettingsToProject(self):
        s = QgsSettings()
        region = s.value("geodata_cz_sk/region", "")
        if region == "":
            QMessageBox.information(None, self.tr("Error"),
                                            self.tr("You have to set region first in the settings."))
        else:
            try:
                self.region_handler.applyTransformations(region, "PROJECT")
                self.iface.messageBar().pushMessage(self.tr("Info"),
                                                               self.tr("Settings sucessfully saved into the project."),
                                                               level=Qgis.Info)
            except Exception as e:
                print(e)
                QMessageBox.information(None, self.tr("Error"),
                                                            self.tr("Can not save settings into the project."))

    def showSettings(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg_region = RegionDialog(self.iface, self.region_handler)
            self.dlg_main = GeoDataDialog(self.iface, self.dlg_region)

        if self.dlg_region is not None:
            self.dlg_region.show()

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg_region = RegionDialog(self.iface, self.region_handler)
            self.dlg_main = GeoDataDialog(self.iface, self.dlg_region)

        s = QgsSettings()
        region = s.value("geodata_cz_sk/region", "")
        if region == "":
            # show the dialog
            self.dlg_region.show()
            # Run the dialog event loop
            result = self.dlg_region.exec_()
            # See if OK was pressed
            if result:
                # Do something useful here - delete the line containing pass and
                # substitute with your code.
                pass
        else:
            # show the dialog
            self.dlg_main.show()
            # Run the dialog event loop
            result = self.dlg_main.exec_()
            # See if OK was pressed
            if result:
                # Do something useful here - delete the line containing pass and
                # substitute with your code.
                pass
