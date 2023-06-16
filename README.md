# SlicerThemes

3D Slicer extensions for creating and applying qt-material based QSS themes

![Screenshot](Screenshot1.png)


## Applying a theme at startup

```` python
# In your .slicerrc.py file
import Themes
logic = Themes.ThemesLogic()

try:
    import qt_material
except:
    logic.installQtMaterial()

templates_list = logic.getAvailableQSSTemplates()
color_list = logic.getAvailableColorFiles()
colorName = 'dark_medical'
color = color_list[colorName]
template_name = 'slicer-material'
template = templates_list[template_name]

print('applying theme: ' + template_name + ' with colors ' + colorName)
logic.applyThemeForSlicer(colors=color, template=template, invert_secondary=False)
````
