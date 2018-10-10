@echo off

call :export_icon router
goto :eof

:export_icon
inkscape -f images.svg -i %~1 -j -w 16 -e icon_16x16.png
inkscape -f images.svg -i %~1 -j -w 20 -e icon_20x20.png
inkscape -f images.svg -i %~1 -j -w 24 -e icon_24x24.png
inkscape -f images.svg -i %~1 -j -w 32 -e icon_32x32.png
inkscape -f images.svg -i %~1 -j -w 40 -e icon_40x40.png
inkscape -f images.svg -i %~1 -j -w 48 -e icon_48x48.png
inkscape -f images.svg -i %~1 -j -w 64 -e icon_64x64.png
inkscape -f images.svg -i %~1 -j -w 72 -e icon_72x72.png
inkscape -f images.svg -i %~1 -j -w 96 -e icon_96x96.png
inkscape -f images.svg -i %~1 -j -w 128 -e icon_128x128.png
goto :eof
