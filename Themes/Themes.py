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
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
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

        self.populateThemesList()
        self.populateStylesList()


        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.ui.clearButton.clicked.connect(self.onClearButton)
        self.ui.ThemeComboBox.currentTextChanged.connect(self.onThemeSelectionChanged)
        self.ui.loadColorThemeButton.clicked.connect(self.onLoadColorThemeButton)
        self.ui.saveThemeButton.clicked.connect(self.onExportButtonClicked)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        

    
    
    
    def onThemeSelectionChanged(self, text):
        self.ui.InvertCheckBox.checked = 'light_' in text

        from qt_material import get_theme

        theme = get_theme(text)

        self.ui.primaryColorPickerButton.setColor(qt.QColor(theme['primaryColor']))
        self.ui.primaryLightColorPickerButton.setColor(qt.QColor(theme['primaryLightColor']))
        self.ui.secondaryColorPickerButton.setColor(qt.QColor(theme['secondaryColor']))
        self.ui.secondaryLightColorPickerButton.setColor(qt.QColor(theme['secondaryLightColor']))
        self.ui.secondaryDarkColorPickerButton.setColor(qt.QColor(theme['secondaryDarkColor']))
        self.ui.primaryTextColorPickerButton.setColor(qt.QColor(theme['primaryTextColor']))
        self.ui.secondaryTextColorPickerButton.setColor(qt.QColor(theme['secondaryTextColor']))

        print(self.ui.secondaryTextColorPickerButton.text)
    
    
    def getThemeDictionary(self):
        theme = {}
        theme['primaryColor'] = self.ui.primaryColorPickerButton.color.name()
        theme['primaryLightColor'] = self.ui.primaryLightColorPickerButton.color.name()
        theme['secondaryColor'] = self.ui.secondaryColorPickerButton.color.name()
        theme['secondaryLightColor'] = self.ui.secondaryLightColorPickerButton.color.name()
        theme['secondaryDarkColor'] = self.ui.secondaryDarkColorPickerButton.color.name()
        theme['primaryTextColor'] = self.ui.primaryTextColorPickerButton.color.name()
        theme['secondaryTextColor'] = self.ui.secondaryTextColorPickerButton.color.name()
        return theme
    
    
    def populateThemesList(self):
        from qt_material import list_themes

        themes = list_themes()

        self.ui.ThemeComboBox.clear()

        for theme in themes:
            self.ui.ThemeComboBox.addItem(theme)
        self.enter()
    
    def populateStylesList(self):
        self.templateDict = self.logic.getAvailableQSSTemplates()
        self.ui.StyleComboBox.clear()

        for name in self.templateDict.keys():
            self.ui.StyleComboBox.addItem(name)
    
    
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
        self.onThemeSelectionChanged(self.ui.ThemeComboBox.currentText)

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
        print('applying')
        self.ui.applyButton.enabled = False
        self.ui.clearButton.enabled = False
        self.ui.applyButton.text = 'Loading theme...'
        slicer.app.processEvents()
        themeDictionary = self.getThemeDictionary()
        self.logic.applyThemeForSlicer(themeDictionary, self.templateDict[self.ui.StyleComboBox.currentText],self.ui.InvertCheckBox.checked)
        self.ui.applyButton.enabled = True
        self.ui.clearButton.enabled = True
        self.ui.applyButton.text = 'Apply Theme'
        print('applying done')

    def onClearButton(self):
        slicer.app.styleSheet = ''

    def onLoadColorThemeButton(self):

        colorThemePath = qt.QFileDialog.getOpenFileName(None,"Open color theme file", "~/", "XML Files (*.xml)")
        self.ui.ThemeComboBox.addItem(colorThemePath)
        self.ui.ThemeComboBox.currentText = colorThemePath

    def onExportButtonClicked(self):
        colorThemePath = qt.QFileDialog.getSaveFileName(None,"Save color theme file", "~/", "XML Files (*.xml)")

        theme = self.getThemeDictionary()
        self.logic.exportThemeFile(theme, colorThemePath)


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
    
    
    def exportThemeFile(self, themeDictionary, themeFileName):

        tempPath = self.createThemeFile(themeDictionary)

        import shutil
        shutil.copyfile(tempPath, themeFileName)

    
    def createThemeFile(self, themeDictionary):
        templatePath = self.resourcePath('theme.xml.template')
        with open(templatePath) as fp:
            contents = fp.read()

        for color, value in themeDictionary.items():
            contents = contents.replace(color+'Key', value)

        tempFilePath = os.path.join(slicer.app.temporaryPath,'theme.xml')

        with open (tempFilePath, 'w') as fp:
            fp.write(contents)

        print(tempFilePath)
        return tempFilePath
    
    
    def applyThemeForSlicer(self,themeDictionary=None, template='Slicer',invert_secondary=True):
        try:
            import qt_material
        except:
            print('Please install qt-material')
            return

        if themeDictionary is None:
            slicer.app.styleSheet = ''
            return
        
        themeFileName = self.createThemeFile(themeDictionary)

        from qt_material import build_stylesheet
        extra = {'density_scale': '-2'}
        stylesheet = build_stylesheet(theme=themeFileName,template=template, extra=extra, invert_secondary=invert_secondary)
        slicer.app.setStyleSheet(stylesheet)
    
    
    def getAvailableQSSTemplates(self):
        templates = os.listdir(self.resourcePath('Templates'))
        templateLookup = {}
        for template in templates:
            parts = template.split('.')
            templateLookup['-'.join(parts[:-2])] = os.path.join(self.resourcePath('Templates'),template )
        return templateLookup

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
