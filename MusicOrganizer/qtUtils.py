from PyQt4 import QtGui;
from . import utils;

#
# Copyright (c) by Patryk Jaworski
# Contact:
# -> E-mail: Patryk Jaworski <skorpion9312@gmail.com>
# -> XMPP/Jabber: skorpion9312@jabber.org
#

def critical(parent, msg):
	QtGui.QMessageBox.critical(parent, 'Music Organizer :: %s' % _('Critical error'), msg, QtGui.QMessageBox.Ok);

def chooseDir(parent, msg):
	return QtGui.QFileDialog.getExistingDirectory(parent, msg, utils.getHomeDir());

