cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerThemes)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/sjh26/SlicerThemes")
set(EXTENSION_CATEGORY "Utilities")
set(EXTENSION_CONTRIBUTORS "Sam Horvath (Kitware Inc)")
set(EXTENSION_DESCRIPTION "This extension allows Material based color themes and styling to be applied to 3D Slicer.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/sjh26/SlicerThemes/main/Screenshot1.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/sjh26/SlicerThemes/main/Themes/Resources/Icons/Themes.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Themes)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
