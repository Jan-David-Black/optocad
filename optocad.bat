python "%~dp0src\PCBToSeg.py" --pcb "%~dpn1.kicad_pcb" --seg "%~dpn1.seg"
python "%~dp0src\SegToSpt.py" --seg "%~dpn1.seg" --spt "%~dpn1_LO.spt" --template "%~dp0templates\template.spt"
python "%~dp0src\NetToPCB.py" --pcb "%~dpn1.kicad_pcb" --net "%~dpn1.net" --template "%~dp0templates\template.kicad_pcb"
rem echo ran python scripts
rem klayout_app -rd input="%~dpn2.gds" -rd output="%~dpn1.dxf" -r "%~dp0src/convert.rb"
