def readTriplet(strTriplet):
    name = strTriplet.split()[0]
    triplet = strTriplet.split()[1:]
    triplet[-1] += ";";
    return name, [float(numeric_string[:-1])*args.scaling_factor for numeric_string in triplet]

def make_path_sane(p):
    """Function to uniformly return a real, absolute filesystem path."""
    # ~/directory -> /home/user/directory
    p = os.path.expanduser(p)
    # A/.//B -> A/B
    p = os.path.normpath(p)
    # Resolve symbolic links
    p = os.path.realpath(p)
    # Ensure path is absolute
    p = os.path.abspath(p)
    return p
    
import argparse
import os.path

parser = argparse.ArgumentParser(description='Convert .net file to kicad pcb file')
parser.add_argument('--net', dest="fname_net", nargs='?', const=1, default='Routing.net', help='the input .net file')
parser.add_argument('--pcb', dest="fname_pcb", nargs='?', const=1, default='Routing.kicad_pcb', help='output file')
parser.add_argument('--seg', dest="fname_segments", nargs='?', const=1, default='Routing.seg', help='segments file')
parser.add_argument('--template', dest="fname_template", nargs='?', const=1, default='template.kicad_pcb', help='template file')
parser.add_argument('--scale', dest="scaling_factor", nargs='?', const=1, type=float, default=1e-3, help='scale_up or down 1e-3 => representation of um as um')
args = parser.parse_args()
#print(args)

#args.fname_net = make_path_sane(args.fname_net)
#args.fname_pcb = make_path_sane(args.fname_net)
#args.fname_segments = make_path_sane(args.fname_segments)
#args.fname_template = make_path_sane(args.fname_template)

template = dict()
template['file'] = open(args.fname_template, 'r')
template['top'] = template['file'].read()
template['file'].close()
template['port'] = '''
(module blank:port (layer Metal2)
  (at {x} {y})
  (pad 1 smd rect (at 0 0) (size 0.01 0.01) (layers Metal2)
    {net})
)'''
template['net'] = '(net {num} {name})\n'
net = dict()
net['file'] = open(args.fname_net, 'r')
net['content'] = net['file'].readlines()
net['file'].close()

name, net['anchor'] = readTriplet(net['content'][2])
net['nets'] = []
i = 4;
while i<len(net['content'])-4:
    curr_net = dict()
    curr_net['name']    = net['content'][i].split()[1]
    name, curr_net['anchor']  = readTriplet(net['content'][i+1])
    name, curr_net['start']   = readTriplet(net['content'][i+2])
    name, curr_net['end']     = readTriplet(net['content'][i+3])
    net['nets'].append(curr_net)
    i+=5

pcb = dict()
pcb['ports'] = ''
pcb['nets'] = ''

for i,curr_net in enumerate(net['nets']):
    net_def = template['net'].format(num = i+1, name = curr_net['name'])
    pcb['nets']+=net_def
    for start_end in ['start', 'end']:
        pcb['ports']+=template['port'].format(net = net_def, x = curr_net[start_end][0],
            y = -1*curr_net[start_end][1])

seg = dict()
seg['content']=''
try:
    seg['file'] =  open(args.fname_segments, 'r')
    seg['content'] = seg['file'].read()
    seg['file'].close()
except BaseException:
    import sys
    #print(sys.exc_info()[0])
    print('.seg file not found; using none')
#    import traceback
#    print(traceback.format_exc())

try:
    pcb['file'] = open(args.fname_pcb, 'w')
    pcb['file'].write(template['top'].format(net_definitions = pcb['nets'], ports = pcb['ports'], segments=seg['content']))
    pcb['file'].close()
except BaseException:
    import sys
    print(sys.exc_info()[0])
    import traceback
    print(traceback.format_exc())
