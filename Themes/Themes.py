import logging
import os

import vtk

import slicer
import qt
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# Themes
#

class Themes(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Themes"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Utilities"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Sam Horvath (Kitware)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This scripted module uses the qt-material package to update the color theme of Slicer.
See more information in <a href="https://github.com/organization/projectname#Themes">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete


#
# Register sample data sets in Sample Data module
#




#
# ThemesWidget
#

class ThemesWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/Themes.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = ThemesLogic()
        

        self.ui.installQtMaterialButton.clicked.connect(self.onInstallQtMaterialButtonClicked)
        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.ui.clearButton.clicked.connect(self.onClearButton)
        self.ui.ColorsComboBox.currentTextChanged.connect(self.onColorsSelectionChanged)
        self.ui.loadColorsButton.clicked.connect(self.onLoadColorsButton)
        self.ui.exportColorsButton.clicked.connect(self.onExportColorsButtonClicked)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        

    def onInstallQtMaterialButtonClicked(self):
        self.logic.installQtMaterial()
        self.checkForQtMaterial()
    
    
    def checkForQtMaterial(self):
        try:
            import qt_material
            self.ui.warningLabel.text = ''
            self.ui.installQtMaterialButton.visible = False
            self.populateColors()
            self.populateTemplates()
            self.ui.applyButton.enabled = True
            return True
        except:
            self.ui.warningLabel.text = 'Please click below to install qt-material'
            self.ui.warningLabel.styleSheet = "color: red;"
            self.ui.applyButton.enabled = False
            self.ui.installQtMaterialButton.visible = True
            return False
            


    def onColorsSelectionChanged(self, text):
        if not text:
            return
        self.ui.InvertCheckBox.checked = 'light_' in text

        from qt_material import get_theme

        path = self.colors[text]

        colors = get_theme(path)

        self.ui.primaryColorPickerButton.setColor(qt.QColor(colors['primaryColor']))
        self.ui.primaryLightColorPickerButton.setColor(qt.QColor(colors['primaryLightColor']))
        self.ui.secondaryColorPickerButton.setColor(qt.QColor(colors['secondaryColor']))
        self.ui.secondaryLightColorPickerButton.setColor(qt.QColor(colors['secondaryLightColor']))
        self.ui.secondaryDarkColorPickerButton.setColor(qt.QColor(colors['secondaryDarkColor']))
        self.ui.primaryTextColorPickerButton.setColor(qt.QColor(colors['primaryTextColor']))
        self.ui.secondaryTextColorPickerButton.setColor(qt.QColor(colors['secondaryTextColor']))

   
    
    def getCurrentColors(self):
        colors = {}
        colors['primaryColor'] = self.ui.primaryColorPickerButton.color.name()
        colors['primaryLightColor'] = self.ui.primaryLightColorPickerButton.color.name()
        colors['secondaryColor'] = self.ui.secondaryColorPickerButton.color.name()
        colors['secondaryLightColor'] = self.ui.secondaryLightColorPickerButton.color.name()
        colors['secondaryDarkColor'] = self.ui.secondaryDarkColorPickerButton.color.name()
        colors['primaryTextColor'] = self.ui.primaryTextColorPickerButton.color.name()
        colors['secondaryTextColor'] = self.ui.secondaryTextColorPickerButton.color.name()
        return colors
    
    
    def populateColors(self):
        from qt_material import list_themes

        self.colors = {}
        colors_list = list_themes()

        for c in colors_list:
            self.colors[c] = c

        self.colors.update(self.logic.getAvailableColorFiles())

        self.ui.ColorsComboBox.clear()

        for color in self.colors:
            self.ui.ColorsComboBox.addItem(color)
    
    def populateTemplates(self):
        self.templates = self.logic.getAvailableQSSTemplates()
        self.ui.TemplateComboBox.clear()

        for name in self.templates.keys():
            self.ui.TemplateComboBox.addItem(name)
    
    
    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        
        self.initializeParameterNode()
        if self.checkForQtMaterial():
            self.onColorsSelectionChanged(self.ui.ColorsComboBox.currentText)

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        

        

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.

        """
        self.ui.applyButton.enabled = False
        self.ui.clearButton.enabled = False
        self.ui.applyButton.text = 'Loading theme...'
        slicer.app.processEvents()
        colors = self.getCurrentColors()
        self.logic.applyThemeForSlicer(colors, self.templates[self.ui.TemplateComboBox.currentText],self.ui.InvertCheckBox.checked)
        self.ui.applyButton.enabled = True
        self.ui.clearButton.enabled = True
        self.ui.applyButton.text = 'Apply Theme'

    def onClearButton(self):
        slicer.app.styleSheet = ''

    def onLoadColorsButton(self):

        colorPath = qt.QFileDialog.getOpenFileName(None,"Open color file", "~/", "XML Files (*.xml)")
        if colorPath:
            name = os.path.basename(colorPath)
            self.colors[name] = colorPath
            self.ui.ColorsComboBox.addItem(name)
            self.ui.ColorsComboBox.currentText = name

    def onExportColorsButtonClicked(self):
        colorPath = qt.QFileDialog.getSaveFileName(None,"Save color file", "~/", "XML Files (*.xml)")
        if colorPath:
            colors = self.getCurrentColors()
            self.logic.exportColorFile(colors, colorPath)


#
# ThemesLogic
#

class ThemesLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def resourcePath(self, filename):
        """Return the absolute path of the module ``Resources`` directory.
        """
        scriptedModulesPath = os.path.dirname(slicer.util.modulePath(self.moduleName))
        return os.path.join(scriptedModulesPath, 'Resources', filename)
    
    
    def installQtMaterial(self):
        slicer.util.pip_install('\'qt-material @ git+https://github.com/sjh26/qt-material@1daabefe7f39d82a510ebeab2f26b3b70c5d7c1c\'')
    
    def exportColorFile(self, colors, colorPath):

        tempPath = self.createColorFile(colors)

        import shutil
        shutil.copyfile(tempPath, colorPath)

    
    def createColorFile(self, colors):
        templatePath = self.resourcePath('theme.xml.template')
        with open(templatePath) as fp:
            contents = fp.read()

        for color, value in colors.items():
            contents = contents.replace(color+'Key', value)

        tempFilePath = os.path.join(slicer.app.temporaryPath,'colors.xml')

        with open (tempFilePath, 'w') as fp:
            fp.write(contents)

        return tempFilePath
    
    
    def applyThemeForSlicer(self,colors, template, invert_secondary=True):
        try:
            import qt_material
        except:
            print('Please install qt-material')
            return

        if isinstance(colors, dict):
            colorPath = self.createColorFile(colors)
        else:
            colorPath = colors

        from qt_material import build_stylesheet
        extra = {'density_scale': '-2'}
        if 'slicer.classic' in template:
            extra['font_family'] = slicer.app.font().family()
            extra['font_size'] = '16'
            print(slicer.app.font().family())
        stylesheet = build_stylesheet(theme=colorPath,template=template, extra=extra, invert_secondary=invert_secondary)
        slicer.app.setStyleSheet(stylesheet)
    
    
    def getAvailableQSSTemplates(self):
        templates = os.listdir(self.resourcePath('Templates'))
        templateLookup = {}
        for template in templates:
            parts = template.split('.')
            templateLookup['-'.join(parts[:-2])] = os.path.join(self.resourcePath('Templates'),template )
        return templateLookup

   
    def getAvailableColorFiles(self):
        colors = os.listdir(self.resourcePath('Colors'))
        colorsLookup = {}
        for color in colors:
            name = os.path.basename(color)
            colorsLookup[name] = os.path.join(self.resourcePath('Colors'),color )
        return colorsLookup

    
    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        pass

    


#
# ThemesTest
#

class ThemesTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_Themes1()

    def test_Themes1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        

        self.delayDisplay('Test passed')
