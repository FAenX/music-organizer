from PyQt4 import QtGui, QtCore;
from . import interface;
from .. import qtUtils;
from .. import utils as utils;
import os;
import sys;
import platform;
import time;
import random;
from collections import deque;

#
# Copyright (c) by Patryk Jaworski
# Contact:
# -> E-mail: Patryk Jaworski <skorpion9312@gmail.com>
# -> XMPP/Jabber: skorpion9312@jabber.org
#

class Organizer(QtGui.QMainWindow, interface.Interface):
	__app = None;
	__statusBar = None;
	__menuBar = None;
	__path = None;
	__target = None;
	__badCharacters = None;
	__recursive = None;
	__copy = None;
	__delete = None;
	__deleteEmpty = None;
	__follow = None;
	__force = None;
	__scheme = None;
	__recognizeCovers = None;
	__normalizeTags = None;
	__downloadLyrics = None;
	__covers = {};
	__numOk = 0;
	__numSkipped = 0;
	__numDeleted = 0;
	__numLeft = 0
	__numCovers = 0;
	__toRemove = [];
	__numUntagged = 0
	__numDuplicates = 0;
	__files = [];
	__progress = None;
	__duplicates = None;
	__dStrategy = None;
	__dAction = None;

	def __init__(self, args):
		self.__app = QtGui.QApplication(args);
		QtGui.QMainWindow.__init__(self);
		utils.ENABLE_VERBOSE = True;
		utils.init();
		self.__initUI();
	
	def operate(self):
		self.show();
		sys.exit(self.__app.exec_());

	# TODO: Add 'detect duplicates option'
	def __initUI(self):
		utils.verbose(_('Initializing UI...'));
		self.setWindowTitle('Music Organizer');
		self.resize(500, 300);
		self.setWindowIcon(QtGui.QIcon('./data/icons/icon.png'));
		self.__statusBar = self.statusBar();
		self.__menuBar = self.menuBar();

		# Toolbar
		start = QtGui.QAction(QtGui.QIcon('./data/icons/start.png'), _('Start'), self);
		start.setStatusTip(_('Start organize'));
		self.connect(start, QtCore.SIGNAL('triggered()'), self.__organize);
		exit = QtGui.QAction(QtGui.QIcon('./data/icons/exit.png'), _('Exit'), self);
		exit.setStatusTip(_('Exit Music Organizer'));
		self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'));
		toolbar = self.addToolBar(_('Start'));
		toolbar.addAction(start);
		toolbar = self.addToolBar(_('Exit'));
		toolbar.addAction(exit);

		# Menubar
		tmp = self.__menuBar.addMenu(_('&File'));
		tmp.addAction(start);
		tmp.addAction(exit);
		tmp = self.__menuBar.addMenu(_('&Help'));
		about = QtGui.QAction(QtGui.QIcon('./data/icons/about.png'), _('About'), self);
		about.connect(about, QtCore.SIGNAL('triggered()'), self.__about);
		tmp.addAction(about);

		# Main content
		container = QtGui.QWidget();
		vbox = QtGui.QVBoxLayout();
		topGrid = QtGui.QGridLayout();
		bottomGrid = QtGui.QGridLayout();
		self.__path = QtGui.QLineEdit();
		self.__path.setText(utils.getHomeDir());
		self.__target = QtGui.QLineEdit();
		self.__scheme = QtGui.QLineEdit();
		self.__scheme.setToolTip('%s: {artist} {album} {date} {title} {old-file-name} {genre} {track}' % _('Available blocks'));
		self.__scheme.setStatusTip('%s: {artist} {album} {date} {title} {old-file-name} {genre} {track}' % _('Available blocks'));
		self.__setDefaultScheme();
		self.__badCharacters = QtGui.QLineEdit();
		self.__badCharacters.setToolTip(_('This characters is used if "Normalize tags" is checked.'));
		self.__badCharacters.setStatusTip(_('This characters is used if "Normalize tags" is checked.'));
		self.__setDefaultBadCharacters();
		self.__replace = QtGui.QLineEdit();
		self.__replace.setToolTip(_('Replacement for any character from "Bad characters". Leave empty if you want to remove all bad characters.'));
		self.__replace.setStatusTip(_('Replacement for any character from "Bad characters". Leave empty if you want to remove all bad characters.'));
		b1 = QtGui.QPushButton(_('Browse'));
		b1.setStatusTip(_('Select search directory'));
		b2 = QtGui.QPushButton(_('Browse'));
		b2.setStatusTip(_('Select target directory'));
		b3 = QtGui.QPushButton(_('Set default'));
		b4 = QtGui.QPushButton(_('Set default'));
		self.connect(b1, QtCore.SIGNAL('clicked()'), self.__browsePath);
		self.connect(b2, QtCore.SIGNAL('clicked()'), self.__browseTarget);
		self.connect(b3, QtCore.SIGNAL('clicked()'), self.__setDefaultScheme);
		self.connect(b4, QtCore.SIGNAL('clicked()'), self.__setDefaultBadCharacters);

		self.__recursive = QtGui.QCheckBox(_('Recursive mode'));	
		self.__recursive.setStatusTip(_('Enable recursive mode'));
		self.__delete = QtGui.QCheckBox(_('Delete mode'));
		self.__delete.setStatusTip(_('Delete filtered directories'));
		self.__deleteEmpty = QtGui.QCheckBox(_('Clean directories'));
		self.__deleteEmpty.setStatusTip(_('Remove all empty directories'));
		self.__force = QtGui.QCheckBox(_('Force'));
		self.__force.setStatusTip(_('Force delete filtered directories'));
		self.__copy = QtGui.QCheckBox(_('Copy'));
		self.__copy.setStatusTip(_('Copy files instead of move'));
		self.__follow = QtGui.QCheckBox(_('Follow symlinks'));
		self.__follow.setStatusTip(_('Follow symlinks/links/shortcuts'));
		self.__normalizeTags = QtGui.QCheckBox(_('Normalize tags'));
		self.__normalizeTags.setStatusTip(_('Remove specified bad characters from tags (~,/,@,# etc.)'));
		self.__recognizeCovers = QtGui.QCheckBox(_('Recognize covers'));
		self.__recognizeCovers.setStatusTip(_('Try to recognize covers'));
		self.__downloadLyrics = QtGui.QCheckBox(_('Download lyrics'));
		self.__downloadLyrics.setStatusTip('%s %s' % (_('[NOT IMPLEMENTED YET]'), _('Find and download lyrics for all tracks')));
		self.__downloadLyrics.setDisabled(True);

		topGrid.setSpacing(10);
		topGrid.addWidget(QtGui.QLabel(_('Search path:')), 1, 0, QtCore.Qt.AlignRight);
		topGrid.addWidget(self.__path, 1, 1);
		topGrid.addWidget(b1, 1, 2);
		topGrid.addWidget(QtGui.QLabel(_('Target path:')), 2, 0, QtCore.Qt.AlignRight);
		topGrid.addWidget(self.__target, 2, 1);
		topGrid.addWidget(b2, 2, 2);
		topGrid.addWidget(QtGui.QLabel(_('Scheme:')), 3, 0, QtCore.Qt.AlignRight);
		topGrid.addWidget(self.__scheme, 3, 1);
		topGrid.addWidget(b3, 3, 2);
		topGrid.addWidget(QtGui.QLabel(_('Bad characters:')), 4, 0, QtCore.Qt.AlignRight);
		topGrid.addWidget(self.__badCharacters, 4, 1);
		topGrid.addWidget(b4, 4, 2);
		topGrid.addWidget(QtGui.QLabel(_('Replacement: ')), 5, 0, QtCore.Qt.AlignRight);
		topGrid.addWidget(self.__replace, 5, 1);

		bottomGrid.addWidget(self.__recursive, 1, 0);
		bottomGrid.addWidget(self.__follow, 1, 1);
		bottomGrid.addWidget(self.__copy, 1, 2);
		bottomGrid.addWidget(self.__delete, 2, 0);
		bottomGrid.addWidget(self.__force, 2, 1);
		bottomGrid.addWidget(self.__deleteEmpty, 2, 2);
		bottomGrid.addWidget(self.__normalizeTags, 3, 0);
		bottomGrid.addWidget(self.__recognizeCovers, 3, 1);
		bottomGrid.addWidget(self.__downloadLyrics, 3, 2);

		duplicatesGrid = QtGui.QGridLayout();

		self.__dStrategy = QtGui.QComboBox();
		self.__dStrategy.addItem('MD5');
		self.__dStrategy.addItem('SHA1');
		self.__dStrategy.addItem(_('File name'));

		self.__dAction = QtGui.QComboBox();
		self.__dAction.addItem(_('Remove'));
		self.__dAction.addItem(_('Leave'));

		duplicatesGrid.addWidget(QtGui.QLabel(_('Strategy:')), 1, 0, QtCore.Qt.AlignRight);	
		duplicatesGrid.addWidget(self.__dStrategy, 1, 1);
		duplicatesGrid.addWidget(QtGui.QLabel(_('Action:')), 2, 0, QtCore.Qt.AlignRight);
		duplicatesGrid.addWidget(self.__dAction, 2, 1);
		duplicatesGrid.setColumnStretch(1, 2);

		self.__duplicates = QtGui.QGroupBox(_('Detect duplicates'));
		self.__duplicates.setCheckable(True);
		self.__duplicates.setChecked(False);
		#self.__duplicates.setDisabled(True);
		self.__duplicates.setLayout(duplicatesGrid);
		#self.__duplicates.setToolTip(_('This functionality was disabled due to terrible bug in 0.1-beta...'));
		self.__duplicates.setStatusTip(_('Detect duplicates and decide what to do.'));

		topGroup = QtGui.QGroupBox(_('Main settings'));
		bottomGroup = QtGui.QGroupBox(_('Options'));
		topGroup.setLayout(topGrid);
		bottomGroup.setLayout(bottomGrid);
		vbox.addWidget(topGroup);
		vbox.addWidget(bottomGroup);
		vbox.addWidget(self.__duplicates);
		container.setLayout(vbox);
		self.setCentralWidget(container);
		
	def __browseTarget(self):
		target = qtUtils.chooseDir(self, _('Select target directory'));
		if target:
			self.__target.setText(target);
	
	def __setDefaultScheme(self):
		self.__scheme.setText('{artist}{0}{album}{0}{title}'.replace('{0}', utils.DIR_SEPARATOR));
	
	def __setDefaultBadCharacters(self):
		self.__badCharacters.setText(utils.BAD_CHARS);

	def __browsePath(self):
		path = qtUtils.chooseDir(self, _('Select search directory'));
		if path:
			self.__path.setText(path);

	def __clean(self):
		self.__numOk = 0;
		self.__numSkipped = 0;
		self.__numLeft = 0
		self.__numDeleted = 0;
		self.__numUntagged = 0;
		self.__numCovers = 0;
		self.__numDuplicates = 0;
		self.__files = [];
		self.__toRemove = [];
		self.__covers = {};
	
	def __startOrganize(self):
		if ('alfa' in utils.getVersion() or 'beta' in utils.getVersion()) and self.__duplicates.isChecked() and self.__dAction.currentText() == _('Remove'):
			result = QtGui.QMessageBox.question(self, 'Music Organizer :: %s' % _('Question'), _('Warning! This is testing version, all actions like \"Remove\" may works unstable. It is strongly recommended to work with copies instead of oryginal files. Do you want to continue?'), 1, 2);
			if result == 2:
				return False;
		self.__clean();
		try:
			utils.prepare(self.__path.text(), self.__target.text());
			if self.__path.text()[-1] != utils.DIR_SEPARATOR:
				self.__path.insert(utils.DIR_SEPARATOR);
			if self.__target.text()[-1] != utils.DIR_SEPARATOR:
				self.__target.insert(utils.DIR_SEPARATOR);
		except Exception as e:
			qtUtils.critical(self, str(e));
			return False;
		utils.verbose(_('Staring hardcore organizing action!'));
		self.__progress = QtGui.QProgressDialog('Initializing...', 'Cancel', 0, 100, self);
		self.__progress.setMinimumDuration(1);
		self.__progress.setAutoClose(False);
		self.__progress.setAutoReset(False);
		self.__progress.forceShow();
		self.__progress.open();
		self.__progress.setValue(0);
		queue = deque([self.__path.text()]);
		try:	
			while len(queue) != 0:
				if self.__progress.wasCanceled():
					raise KeyboardInterrupt(_('Canceled'));
				path = queue.popleft();
				try:
					files = os.listdir(path);
					if len(files) == 0:
						if self.__deleteEmpty.isChecked():
							self.__remove(path);
						else:
							utils.verbose(_('Skipping empty directory %s') % path);
						continue;
				except OSError:
					utils.verbose(_('Unable to list directory %s') % path);
					continue;
				hasMusicFiles = False;
				for f in files:
					if self.__progress.wasCanceled():
						raise KeyboardInterrupt(_('Canceled'));
					if os.path.islink(path + f) and not self.__follow.isChecked():
						utils.verbose(_('Skipping link %s...') % (path + f))
						continue;
					if os.path.isdir(path + f) and self.__recursive.isChecked():
						queue.append(path + f + utils.DIR_SEPARATOR);
						if self.__delete.isChecked() and path not in self.__toRemove:
							self.__toRemove.append(path);
						continue;
					if f[-4:].lower() == '.mp3':
						print('[I] %s' % _('Adding %s') % (path + f));
						if self.__delete.isChecked() and path not in self.__toRemove:
							self.__toRemove.append(path);
						self.__files.append(path + f);
						self.__progress.setLabelText(_('Preparing files (%d)') % len(self.__files));
						newMax = 0.9 if random.choice((0, 1, 2)) == 1 else 0.7;
						if len(self.__files) > self.__progress.maximum() * newMax:
							self.__progress.setMaximum(int(len(self.__files)) * 2);
						self.__progress.setValue(len(self.__files));
						hasMusicFiles = True;
						continue;
					if f[f.rfind('.'):].lower() in ('.jpg', '.gif', '.png', '.bmp', '.jpeg'):
						dirname = os.path.dirname(path + f);
						if dirname not in self.__covers:
							self.__covers[dirname] = [];
						self.__covers[dirname].append(f);
				if not hasMusicFiles and path[0:-1] in self.__covers:
					del(self.__covers[path[0:-1]]);

		except KeyboardInterrupt:
			return False;
		utils.verbose(_('Number of files: %d') % len(self.__files));
		self.__numLeft = len(self.__files);
		self.__progress.setMaximum(self.__numLeft);
		if self.__numLeft != 0:
			self.__progress.setValue(0);
			self.__progress.setLabelText(_('Organizing files...'));
		else:
			self.__progress.setMaximum(1);
			self.__progress.setValue(self.__progress.maximum());
			self.__progress.setLabelText(_('No music files found!'));
			self.__progress = None;
			return True;
		try:
			# Initialize duplicates detector
			detector = None;
			if self.__duplicates.isChecked():
				selected = _(self.__dStrategy.currentText());
				available = {_('MD5'): utils.md5, _("SHA1"): utils.sha1, _("File name"): utils.basic};
				detector = utils.duplicatesDetector(available[selected]());
				detector.reset();

			for F in self.__files:
				skip_move = False;
				if self.__progress.wasCanceled():
					raise KeyboardInterrupt();
				D = os.path.dirname(F);

				# Get tags
				tag = utils.getTag(F, True);
				if not tag:
					self.__numUntagged += 1;
					tag = utils.getDefaultTag(F);
				if self.__normalizeTags.isChecked():
					utils.BAD_CHARS = self.__badCharacters.text();
					utils.REPLACE_WITH = self.__replace.text();
					tag = utils.normalizeTags(tag);

				# Detect duplicates
				if self.__duplicates.isChecked():
					result = detector.feed(F);
					if result:
						dups = detector.get(F);
						print('[I] ' + _('Found duplicate.'));
						print('   -> ' + _('First occurrence') + ': %s' % detector.get(F)[0]);
						print('   -> %s' % _('Duplicates:'));
						for dup in dups[1:]:
							print('      -> %s' % dup);
						if self.__dAction.currentText() == _('Remove'):
							try:
								print('[I] ' + _('Removing duplicate %s') % F);
								os.remove(F);
							except OSError:
								print('[W] ' + _('Unable to remove duplicate: %s') % F);
						elif self.__dAction.currentText() == _('Leave'):
							print('[I] ' + _('Skipping duplicate %s') % F);
						self.__numDuplicates += 1;
						self.__numSkipped += 1;
						skip_move = True;

				if not skip_move:	
					if utils.moveTrack(F, tag, self.__target.text(), self.__scheme.text(), self.__copy.isChecked()):
						self.__numOk += 1;
					else:
						self.__numSkipped += 1;

				#!TODO: What about cover duplicates?!
				# Move covers
				if D in self.__covers:
					covers = [];
					for cover in self.__covers[D]:
						covers.append(D + utils.DIR_SEPARATOR + cover);
					outputDir = os.path.dirname(self.__target.text() + self.__scheme.text().format(**tag));
					del(self.__covers[D]);
					moved = utils.moveCovers(covers, outputDir, self.__copy.isChecked());
					self.__numCovers += moved;
				self.__numLeft -= 1;

				self.__progress.setValue(self.__progress.value() + 1);
				self.__updateProgressLabel();
			try:
				while True:
					R = self.__toRemove.pop();
					self.__remove(R);
					self.__updateProgressLabel();
			except IndexError:
				pass;
		except KeyboardInterrupt:
			return False;
		self.__progress.setCancelButtonText(_('Ok'));
		self.__progress = None;
		return True;

	def __updateProgressLabel(self, label = None):
		if not label:
			info = [];
			info.append((_('Total'), len(self.__files)));
			info.append((_('Left'), self.__numLeft));
			info.append((_('Copied') if self.__copy.isChecked() else _('Moved'), self.__numOk))
			info.append((_('Skipped'), self.__numSkipped));
			info.append((_('Removed'), self.__numDeleted));
			info.append((_('Untagged'), self.__numUntagged));
			if self.__recognizeCovers.isChecked():
				info.append((_('Covers copied') if self.__copy.isChecked() else _('Covers moved'), self.__numCovers));
			if self.__duplicates.isChecked():
				info.append((_('Duplicates'), self.__numDuplicates));
			label = '';
			for pair in info:
				label += '<p align="center">%s: <b>%d</b></p>' % (pair[0], pair[1]);
		self.__progress.setLabelText(label);

	def __remove(self, path):
		try:
			utils.verbose(_('Removing %s') % path);
			os.rmdir(path);
			self.__numDeleted += 1;
			return True;
		except Exception:
			utils.verbose(_('Cannot remove %s') % path);
			try:
				if self.__force.isChecked():
					print(_('Force remove...'));
					if self.__path.text() == self.__target.text() and path == self.__path:
						print('[W] %s' % 'Remove: skipping %s' % path);
						return False;
					utils.verbose(_('Force removing %s') % path);
					os.removedirs(path);
					self.__numDeleted += 1;
					return True;
				else:
					raise Exception();
			except:
				print('[W] %s' % _('Unable to remove directory %s...') % path);
		return False;

	def __organize(self):
		if self.__progress != None:
			qtUtils.critical(self, _('Another hardcore organizing action is running now!'));
			return False;
		self.centralWidget().setDisabled(True);
		self.__startOrganize();
		self.centralWidget().setDisabled(False);

	def __about(self):
		QtGui.QMessageBox.about(self, 'Music Organizer :: %s' % _('About'),
		"""<b>Music Organizer</b> v{0}
		<p>Copyright &copy; by Patryk Jaworski &lt;skorpion9312@gmail.com&gt;</p>
		<p>{5}</p>
		<p>Python {1} - Qt {2} - PyQt {3} on {4}</p>""".format(utils.getVersion(), platform.python_version(), QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system(), _('Automatically organize your music collection')));

