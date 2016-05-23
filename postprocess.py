import platform
import subprocess
import sys


def convert_to_mem(filename):
    last_addr = -1
    lines = []
    with open(filename + '.p', 'r') as inp:
        for line in inp.readlines():
            if not line[:21].strip():
                continue
            addr = int(line[:8], 16) if line[:8].strip() else (last_addr + 4)
            if addr != last_addr + 4:
                lines.append('@%04X' % addr)
            lines.append(line[10:21])
            last_addr = addr

    with open(filename + '.mem', 'w') as out:
        out.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Incorrect program call')
    filename = sys.argv[1].rsplit('.', maxsplit=1)[0]
    convert_to_mem(filename)
    cmd_list = ['data2mem.exe', '-bm', 'resources/frisc_bram.bmm', '-bt',
                'resources/world_wrapper.bit', '-bd', filename + '.mem',
                'tag', 'bram_single_macro_inst', '-o', 'b', filename + '.bit']
    if platform.system() == 'Linux':
        cmd_list.insert(0, 'wine')
    subprocess.call(cmd_list)
