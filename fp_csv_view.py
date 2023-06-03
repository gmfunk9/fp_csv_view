import sys, csv, signal, markdown, argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QHeaderView, QAbstractScrollArea,QAbstractItemView
from PyQt5.QtCore import QTimer, Qt, QEvent, QPoint
from PyQt5.QtGui import QColor, QCursor,QWheelEvent
from qt_material import apply_stylesheet

class ScrollTextEdit(QTextEdit):

	def __init__(self, parent=None):
		super().__init__(parent)

	def event(self, event):
		if event.type() == QEvent.KeyPress:
			if event.modifiers() & Qt.ShiftModifier:
				if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
					event.ignore()
					return True
				elif event.key() == Qt.Key_Left:
					horizontal_bar = self.horizontalScrollBar()
					if horizontal_bar:
						horizontal_bar.setValue(horizontal_bar.value() - horizontal_bar.singleStep())
					return True
				elif event.key() == Qt.Key_Right:
					horizontal_bar = self.horizontalScrollBar()
					if horizontal_bar:
						horizontal_bar.setValue(horizontal_bar.value() + horizontal_bar.singleStep())
					return True
		return super().event(event)

class ScrollableTableWidget(QTableWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
		self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

	def wheelEvent(self, event):
		modifiers = QApplication.keyboardModifiers()
		if modifiers == Qt.KeyboardModifier.ShiftModifier:
			event = QWheelEvent(event.position(), event.globalPosition(), event.pixelDelta(), QPoint(event.angleDelta().y() // 30, event.angleDelta().x() // 30), event.buttons(), event.modifiers(), event.phase(), event.inverted())
		else:
			event = QWheelEvent(event.position(), event.globalPosition(), event.pixelDelta(), QPoint(event.angleDelta().x() // 30, event.angleDelta().y() // 30), event.buttons(), event.modifiers(), event.phase(), event.inverted())
		super().wheelEvent(event)

class MainWindow(QMainWindow):

	def __init__(self, filename, darkmode):
		super().__init__()
		self.setup_window()
		self.csv_data = self.load_csv(filename)
		self.sort_order = [None] * len(self.csv_data[0])
		self.setup_table()
		self.darkmode = darkmode
		self.new_windows = []

	def eventFilter(self, source, event):
		if (event.type() == QEvent.Wheel and
			QApplication.keyboardModifiers() == Qt.ShiftModifier):
			degrees = event.angleDelta().y() / 5
			steps = degrees / 5
			if source.horizontalScrollBar().isVisible():
				source.horizontalScrollBar().setValue(source.horizontalScrollBar().value() - int(steps))
			return True
		return super(MainWindow, self).eventFilter(source, event)

	def setup_window(self):
		self.setWindowTitle("CSV Viewer")
		self.resize(640, 480)  

	def load_csv(self, filename):
		with open(filename, 'r') as file:
			return list(csv.reader(file))

	def setup_table(self):
		self.table = ScrollableTableWidget()
		header_row = self.csv_data[0]
		data_rows = self.csv_data[1:]
		self.table.setRowCount(len(data_rows))
		self.table.setColumnCount(len(header_row))
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
		self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		for i, row in enumerate(data_rows):
			for j, item in enumerate(row):
				self.table.setItem(i, j, QTableWidgetItem(str(item)))
		self.table.setHorizontalHeaderLabels(header_row)
		self.table.verticalHeader().setDefaultSectionSize(50)
		self.table.setSortingEnabled(True)
		self.table.horizontalHeader().sectionClicked.connect(self.header_clicked)
		header = self.table.horizontalHeader()
		self.table.setHorizontalHeader(header)
		header.setSortIndicator(-1, Qt.AscendingOrder) 
		self.table.cellDoubleClicked.connect(self.open_cell) 
		self.setCentralWidget(self.table)

	def header_clicked(self, logical_index):
		order = Qt.AscendingOrder if self.sort_order[logical_index] is None or self.sort_order[logical_index] == Qt.DescendingOrder else Qt.DescendingOrder
		self.table.setSortingEnabled(True)
		self.table.sortByColumn(logical_index, order)
		self.table.setSortingEnabled(False)
		self.sort_order[logical_index] = order
		header = self.table.horizontalHeader()
		header.setSortIndicator(logical_index, order)

	def populate_table(self):
		for i, row in enumerate(self.csv_data):
			for j, item in enumerate(row):
				self.table.setItem(i, j, QTableWidgetItem(str(item)))
				self.table.item(i, j).setTextAlignment(Qt.AlignTop)  

	def open_cell(self, row, column):
		new_window = self.create_new_window(row + 1, column)
		self.new_windows.append(new_window)  

	def create_new_window(self, row, column):
		new_window = QWidget()
		new_window.setWindowFlag(Qt.WindowStaysOnTopHint)
		new_window.setGeometry(QCursor.pos().x(), QCursor.pos().y(), 640, 480)
		text, render_md, show_html = self.setup_text_widget(new_window, row, column)
		button_layout = self.create_button_layout(new_window, text, row, column, render_md, show_html)
		self.setup_main_layout(new_window, button_layout, text)
		new_window.show()
		return new_window

	def setup_text_widget(self, new_window, row, column):
		text = QTextEdit(new_window)
		text.setReadOnly(True)
		text.setTextColor(QColor('white')) if self.darkmode else text.setTextColor(QColor('black'))
		render_md = [False]
		show_html = [False]
		self.update_content(text, self.csv_data[row][column], render_md[0], show_html[0])
		# Install event filter
		text.installEventFilter(self)
		return text, render_md, show_html

	def create_button_layout(self, new_window, text, row, column, render_md, show_html):
		button_layout = QHBoxLayout()
		self.create_buttons(new_window, text, button_layout, row, column, render_md, show_html)
		return button_layout

	def create_buttons(self, new_window, text, button_layout, row, column, render_md, show_html):
		self.add_button_to_layout(button_layout, new_window, "Toggle Render", 
								lambda: self.toggle_render(text, self.csv_data[row][column], render_md, show_html))
		self.add_button_to_layout(button_layout, new_window, "Toggle HTML", 
								lambda: self.toggle_html(text, self.csv_data[row][column], render_md, show_html))
		self.add_button_to_layout(button_layout, new_window, "Toggle Word-Wrap", 
								lambda: self.toggle_word_wrap(text))

	def add_button_to_layout(self, button_layout, new_window, button_label, callback):
		button = QPushButton(button_label, new_window)
		button.setStyleSheet("border-width: 1px;")
		button.clicked.connect(callback)
		button_layout.addWidget(button)

	def setup_main_layout(self, new_window, button_layout, text):
		main_layout = QVBoxLayout()
		main_layout.addLayout(button_layout)
		main_layout.addWidget(text)
		new_window.setLayout(main_layout)

	def toggle_render(self, text, value, render_md, show_html):
		render_md[0] = not render_md[0]
		show_html[0] = False if render_md[0] else show_html[0]
		self.update_content(text, value, render_md[0], show_html[0])

	def toggle_html(self, text, value, render_md, show_html):
		show_html[0] = not show_html[0]
		render_md[0] = False if show_html[0] else render_md[0]
		self.update_content(text, value, render_md[0], show_html[0])

	def toggle_word_wrap(self, text):
		text.setLineWrapMode(QTextEdit.NoWrap if text.lineWrapMode() == QTextEdit.WidgetWidth else QTextEdit.WidgetWidth)

	def update_content(self, text, value, render_md, show_html):
		color = 'white' if self.darkmode else 'black'
		if render_md:
			text.setHtml('<style>*{color: ' + color + '; }</style>' + markdown.markdown(value))
		elif show_html:
			text.setPlainText(markdown.markdown(value))
		else:
			text.setPlainText(value)

def main():
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	args = parse_command_line_args()
	app = QApplication(sys.argv)
	setup_app_theme(app, args.darkmode)
	mw = MainWindow(args.filename, args.darkmode)
	mw.show()
	sys.exit(app.exec())

def parse_command_line_args():
	parser = argparse.ArgumentParser(description='CSV Viewer')
	parser.add_argument('filename', help='the CSV file to display')
	parser.add_argument('-d', '--darkmode', action='store_true', help='use the dark mode theme')
	return parser.parse_args()

def setup_app_theme(app, darkmode):
	theme = 'dark_purple.xml' if darkmode else 'light_blue.xml'
	apply_stylesheet(app, theme=theme)
if __name__ == "__main__":
	main()
