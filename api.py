from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QPushButton, QLabel, QFileDialog

from PyQt5.QtGui import QPixmap

from PyQt5 import QtCore

from PyQt5.QtGui import QPainter #, QCursor
from PyQt5.QtWidgets import QHBoxLayout, QSizeGrip, QRubberBand

from PyQt5.QtWidgets import QMenu

import sys

class ResizableRubberBand(QLabel):
    def __init__(self, parent=None):
        super(ResizableRubberBand, self).__init__(parent)
        
        self.setGeometry(0, 0, 200, 200) # starting selected area
        self.newCoordinates()

        self.draggable = True
        self.dragging_threshold = 5
        self.mousePressPos = None
        self.mouseMovePos = None
        self.borderRadius = 5
        self.no_movement = True
                         
        self.setWindowFlags(QtCore.Qt.SubWindow)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(
            QSizeGrip(self), 0, # resize handler
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop) # position of handler
        layout.addWidget(
            QSizeGrip(self), 0, # resize handler
            QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom) # position of handler
        self._band = QRubberBand( # selection boundary
            QRubberBand.Rectangle, self)
                               
        self._band.show() # show the blue filing
        self.show() # show the rectangle

    # Event Handlers    
    def resizeEvent(self, event):
        if self.checkOutOfBounds():
            event.ignore()
        else:
            self._band.resize(self.size())
            self.newCoordinates()

    def paintEvent(self, event):
        # Get current window size
        window_size = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.drawRoundedRect(0, 0, window_size.width(), window_size.height(),
                           self.borderRadius, self.borderRadius)
        qp.end()

    def mousePressEvent(self, event):
        if self.checkOutOfBounds():
            event.ignore()
        else:
            if self.draggable and event.button() == QtCore.Qt.RightButton:
                self.mousePressPos = event.globalPos()                # global position of selected point on screen 
                                                                        # self.pos() local position of selected point
                                                                        # (x : pixels*left->right, y : pixels*top->bottom)
                self.mouseMovePos = event.globalPos() - self.pos()    # global position of widget's upper left corner
            
        super(ResizableRubberBand, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.checkOutOfBounds():
            event.ignore()
        else:
            if self.draggable and event.buttons() and QtCore.Qt.RightButton:
                globalPos = event.globalPos()
                moved = globalPos - self.mousePressPos # where did we move the rectangle relatively to the starting point
                if moved.manhattanLength() > self.dragging_threshold: 
                    # Move when user drag window more than dragging_threshold
                    diff = globalPos - self.mouseMovePos
                    self.move(diff) # move the rectangle
                    self.mouseMovePos = globalPos - self.pos()
                                
        super(ResizableRubberBand, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.checkOutOfBounds():
            event.ignore()
            self.newCoordinates()
        else:
            if self.mousePressPos is not None:
                if event.button() == QtCore.Qt.RightButton:
                    moved = event.globalPos() - self.mousePressPos
                    if moved.manhattanLength() > self.dragging_threshold:
                        # Do not call click event or so on
                        self.no_movement = False
                        event.ignore()
                    else:
                        self.no_movement = True
                    self.mousePressPos = None
                
        self.newCoordinates()
                
        super(ResizableRubberBand, self).mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        if self.no_movement == True:
            contextMenu = QMenu(self)
            deleteAction = contextMenu.addAction('delete')
            exitAction = contextMenu.addAction('exit')        
            
            action = contextMenu.exec_(self.mapToGlobal(event.pos()))
            
            if action == exitAction:
                pass
            elif action == deleteAction:
                self.setParent(None)
                
        super(ResizableRubberBand, self).contextMenuEvent(event)
            
    # regular methods
    def newCoordinates(self):
        self.upper_left = [self.x(), self.y()] 
        self.upper_right = [self.x(), self.y() + self.width()]
        self.lower_right = [self.x() + self.width(), self.y() + self.height()]
        self.lower_left = [self.x() + self.height(), self.y()]
        self.coordinates = [self.upper_left, self.upper_right, self.lower_right, self.lower_left]
        #print('Local Coordinates:', self.coordinates)
        
    def checkOutOfBounds(self):
        if (self.x()<0 or self.y()<0):
            self.setGeometry(0,0,self.size().width(), self.size().height())
            #print ('Cursor global pos:', QCursor.pos())
            #print ('Cursor local pos:', self.mapFromGlobal(QCursor.pos()))
            #QCursor.setpos(x, y)
            return(1)
        elif ( ((self.x() + self.width())>600)  or ((self.y() + self.height())>400) ):
            self.setGeometry(600-self.size().width(),400-self.size().height(),self.size().width(), self.size().height())
            return(1)
        else:
            return(0)
                    
        
class MainWindow(QMainWindow): # child class inherits from QMainWindow

    width = 800
    height = 600
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.initGUI()
    
    def initGUI(self):
        # resize my window
        self.resize(self.width, self.height)
        
        # create main window and add title
        self.window = QWidget()

        # initiate layout preference
        self.layout = QVBoxLayout(self.window) # vertical layout
        
        # create additional widgets
        self.uploadButton()
        self.selectButton()
        
        # set layout
        self.layout.addWidget(self.upload_button)
        self.layout.addWidget(self.select_button)
            
        # finalize window
        self.setCentralWidget(self.window)
        
        # name my main window
        self.setWindowTitle("Load Picture")     
        
    # upload button
    def uploadButton(self):
        self.upload_button = QPushButton('Upload Picture', self.window)
        self.upload_button.clicked.connect(self.getImage)
     
    # image load
    def getImage(self):
        self.upload_button.setEnabled(False)
        
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                               '',
                                               "Image files (*.jpg *.png)")
        #if fname:
        #    print("Your file:", fname, '\n', fname[0])

        imagePath = fname[0]
        self.pixmap = QPixmap(imagePath).scaled(600, 400) # add picture and rescale to 800x600 pixels
        self.label = QLabel("Picture")  
        self.label.setPixmap(self.pixmap)
        self.label.setFixedSize(600,400)
        #self.label.setScaledContents(True) # if I want my picture to be able to scale
        self.layout.addWidget(self.label)
        
    # select button
    def selectButton(self):
        self.select_button = QPushButton('Select Area', self.window)
        self.select_button.clicked.connect(self.handleSelectButton)
            
    # select area
    def handleSelectButton(self):
        ResizableRubberBand(self.label)

def main():
    app = QApplication([])
    # app.setApplicationName('My Picture App')
    
    application = MainWindow()
    
    application.show()
    
    sys.exit(app.exec())
    

if __name__ == '__main__':
    main()