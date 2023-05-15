import argparse

parser = argparse.ArgumentParser(description='extract segments and vias from kicad_pcb file')
parser.add_argument('--pcb', dest="fname_pcb", nargs='?', const=1, default='Routing.kicad_pcb', help='input file')
parser.add_argument('--seg', dest="fname_segments", nargs='?', const=1, default='Routing.seg', help='output file')
args = parser.parse_args()

pcb= dict()
pcb['file'] = open(args.fname_pcb, 'r')
pcb['lines'] = reversed(pcb['file'].readlines())
pcb['file'].close()
started = False

seg = []
for line in pcb['lines']:
    if 'via' in line or 'segment' in line:
        started = True
        seg.append(line)
    elif started:
        break

broken = False
for line in seg:
    if 'uvia' in line:
        broken = True
        break;
if not broken:
    seg_file = open(args.fname_segments, 'w')
    seg_file.writelines(reversed(seg))
    seg_file.close()
else:
    print('The PCB file does not contain segments')
