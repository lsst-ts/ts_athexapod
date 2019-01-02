
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QListWidget

class ApplicationPaginationWidget(QWidget):
    def __init__(self, ATHexapod):
        QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QHBoxLayout()
        self.listLayout = QVBoxLayout()
        self.pageLayout = QStackedLayout()
        self.layout.addLayout(self.listLayout)
        self.layout.addLayout(self.pageLayout)
        self.setLayout(self.layout)

        self.pageList = QListWidget()
        self.pageList.itemSelectionChanged.connect(self.changePage)
        self.listLayout.addWidget(self.pageList)
        self.pages = []
        self.activePage = None

    def setPageListWidth(self, width):
        self.pageList.setFixedWidth(width)

    def addPage(self, text, widget):
        widget.setPageActive(False)
        self.pages.append([text, widget])
        self.pageList.addItem(text)
        self.pageLayout.addWidget(widget)
        if len(self.pages) == 1:
            self.pageList.setCurrentRow(0)

    def changePage(self):
        if self.activePage is not None:
            self.activePage.setPageActive(False)
        items = self.pageList.selectedItems()
        if len(items) > 0:
            text = items[0].text()
            for pages in self.pages:
                if pages[0] == text:
                    self.pageLayout.setCurrentWidget(pages[1])
                    self.activePage = pages[1]
                    self.activePage.setPageActive(True)