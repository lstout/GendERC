import re
import subprocess
import sys
from threading import Timer


def kill_proc(proc, timeout):
    timeout["value"] = True
    proc.kill()


def run(cmd, timeout_sec):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = {"value": False}
    timer = Timer(timeout_sec, kill_proc, [proc, timeout])
    timer.start()
    stdout, stderr = proc.communicate()
    timer.cancel()
    return proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"), timeout["value"]


def extract_text_pdf(pdf_path):
    ret_code, out, err, timeout = run(['ruby', 'pdf_reader.rb', pdf_path], 10)
    if err:
        raise IOError('Could not convert ' + pdf_path + ' to simple text.\n %s' % err)
    if timeout:
        raise IOError('Could not convert ' + pdf_path + ' to simple text due to timeout\n')
    out = re.sub(r' {2,}', ' ', out)
    out = re.sub(r'(\n)+', '\n', out)
    out = re.sub(r'(^[\s])?\n(^[\s])?', ' \n ', out)
    return out

if __name__ == '__main__':
    print extract_text_pdf(sys.argv[1])
