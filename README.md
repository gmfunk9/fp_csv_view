# FP CSV View

This Python application uses PyQt5 to create a graphical user interface (GUI) for viewing CSV files. It provides additional features such as dark mode, markdown rendering, HTML rendering, and text wrapping.

## Installation

To install dependencies, run:

~~~shell
pip install PyQt5 qt_material markdown argparse
~~~

## Usage

The application can be run from the command line with:

~~~shell
python main.py filename.csv
~~~

Optional arguments are:

- `-d`, `--darkmode`: Use the dark mode theme.

For example:

~~~shell
python main.py filename.csv -d
~~~

This will run the program using a dark theme.

## Features

The application provides several key features:

- Viewing a CSV file in a table format.
- Resizing columns interactively.
- Sorting columns in ascending or descending order.
- Opening a cell in a new window by double-clicking.
- In the new window, you can:
  - Toggle markdown rendering.
  - Toggle HTML rendering.
  - Toggle word wrapping.

## Code Explanation

Here is a brief explanation of the key classes and functions in the code:

~~~python
import sys, csv, signal, markdown, argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QHeaderView, QAbstractScrollArea,QAbstractItemView
from PyQt5.QtCore import QTimer, Qt, QEvent, QPoint
from PyQt5.QtGui import QColor, QCursor,QWheelEvent
from qt_material import apply_stylesheet
~~~

The script imports necessary modules, including PyQt5 for the GUI, markdown for rendering markdown text, and argparse for parsing command-line arguments.

`class ScrollTextEdit(QTextEdit)` and `class ScrollableTableWidget(QTableWidget)` modify PyQt5 widgets to have customized scroll behaviors.

`class MainWindow(QMainWindow)` is the main window for the application, which contains the table view of the CSV file. It has functions for setting up the window and table, loading the CSV file, sorting columns, opening a cell in a new window, and more.

`def main()` is the entry point for the application. It sets up the application, parses command-line arguments, and starts the PyQt5 event loop.

`def parse_command_line_args()` is a helper function for parsing command-line arguments.

`def setup_app_theme(app, darkmode)` applies a theme to the application.

## Known Issues and Limitations

- The application currently does not support CSV files with more complex structures such as multi-line cells or nested commas within double quotes.
- It requires a CSV file as input. If a non-CSV file is provided, it will result in an error.

## License

This project is licensed under the terms of the MIT license.
