import argparse
import numpy as np
import os

parser = argparse.ArgumentParser(description='Convert .net file to kicad pcb file')
parser.add_argument('--spt', dest="fname_spt", nargs='?', const=1, default='Routing_LO.spt', help='the output .spt file')
parser.add_argument('--template', dest="fname_template", nargs='?', const=1, default='template.spt', help='template for the .spt file')
parser.add_argument('--seg', dest="fname_seg", nargs='?', const=1, default='Routing.seg', help='input segments file')
parser.add_argument('--scale', dest="scaling_factor", nargs='?', const=1, type=float, default=1e3, help='scale_up or down 1e3 => representation of um as um')
args = parser.parse_args()

template = dict()
template['layer_lookup'] = {'Metal1':'Met1', 'Metal2': 'Met2'}
template['segment']="""
    mask::CSselect("{layer}");
    ml::champheredStraight(cin->this@ANCHOR+[{x_in}, {y_in}, {angle}], cout->this@ANCHOR+[{x_out}, {y_out}, {angle}]: {width});
"""#ml::Straight(cin->this@ANCHOR+[{x_in}, {y_in}, {angle}], cout->this@ANCHOR+[{x_out}, {y_out}, {angle}]: wfix({width}));
template['via']="""
    mask::CSselect("{layer}");
    ml::champheredStraight(cin->this@ANCHOR+[{x}, {y}], cout->this@ANCHOR+[{x}, {y}]: {size});
"""#ml::Straight(ccen->this@ANCHOR+[{x}, {y}]: wfix({size}), {size});
template['file'] = open(args.fname_template, 'r')
template['content'] = template['file'].read()
template['file'].close()

def generateSegment(params):
    layer = template['layer_lookup'][params[3][:-1].split()[-1]]
    width = float(params[2][:-1].split()[-1])*args.scaling_factor
    x_in  = float(params[0][:-1].split()[1] )*args.scaling_factor
    x_out = float(params[1][:-1].split()[1] )*args.scaling_factor
    y_in  = -1*float(params[0][:-1].split()[-1])*args.scaling_factor
    y_out = -1*float(params[1][:-1].split()[-1])*args.scaling_factor

    dx = x_out - x_in
    dy = y_out - y_in
    angle = np.rad2deg(np.arctan2(dy, dx))
    #x_in -= width/2.0 * np.cos(np.deg2rad(angle))
    #x_out+= width/2.0 * np.cos(np.deg2rad(angle))
    #y_in -= width/2.0 * np.sin(np.deg2rad(angle))
    #y_out+= width/2.0 * np.sin(np.deg2rad(angle))
    return template['segment'].format(
        layer = layer, width = width,
        x_in = x_in, x_out = x_out,
        y_in = y_in, y_out = y_out,
        angle = angle
    )

def generateVia(params):
    layer = "Via2" #TODO make dependent on layer names
    power = [1,5,9,13,17,21,25,29]; #only for testing
    
    x    = float(params[0][:-1].split()[1] )*args.scaling_factor
    y    = -1*float(params[0][:-1].split()[-1])*args.scaling_factor
    #size = float(params[1][:-1].split()[-1])*args.scaling_factor
    size = 11 if int(params[4][:-1].split()[-1]) in power else 6
    return template['via'].format(
        layer = layer,
        x = x, y = y, size = size
    )


try:
    seg = dict()
    seg['file'] = open(args.fname_seg, 'r')
    seg['content'] = seg['file'].readlines()
    seg['file'].close()
except:
    print('failed to read .spt file; probably not generated yet')
    import sys
    sys.exit()

spt = dict()
spt['routing'] = ''

import re
for line in seg['content']:
    no_pad = re.findall(r'\(.*\)', line)[0][1:]
    declaration = no_pad.split()[0]
    params = re.findall(r'\(.*?\)',no_pad)
    if declaration == "segment":
        spt['routing'] += generateSegment(params)
    elif declaration == "via":
        spt['routing'] += generateVia(params)
    else:
        print('there was a problem with the seg file...')

spt['file'] = open(args.fname_spt, 'w')
(file, ext) = os.path.splitext(os.path.basename(args.fname_spt))
spt['file'].write(template['content'].format(routing = spt['routing'], name = file))
spt['file'].close()
