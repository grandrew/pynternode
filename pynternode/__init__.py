import pexpect
import json
import re

# 7-bit and 8-bit C1 ANSI sequences
ansi_escape_8bit = re.compile(
    br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
)

class NodeJSRepl:

    def __init__(self, async_repl_executable="./node_modules/.bin/async-repl"):
        try:
            self.nodejs = pexpect.spawn(async_repl_executable)
            self.nodejs.expect("async>")
        except:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Please make sure async-repl is installed in {async_repl_executable}")
    
    def _wait_finish(self):
        self.nodejs.expect("async>")
    
    def execl(self, cmdline):
        print("Sending line to nodejs:", cmdline)
        self.nodejs.sendline(cmdline)
    
    def run(self, cmdline):
        self.execl(cmdline)
        self._wait_finish()
    
    def ret_raw(self, cmdline):
        self.execl(cmdline)
        out = self.nodejs.readline()
        out = self.nodejs.readline()
        out = ansi_escape_8bit.sub(b'', out).strip()
        self._wait_finish()
        print(out)
        return out

    def ret_int(self, cmdline):
        out = "<incomplete>"
        try:
            out = self.ret_raw(cmdline)
            return int(out)
        except:
            raise ValueError(f"Could not parse result {out}")

    def ret_float(self, cmdline):
        return float(self.ret_raw(cmdline))
    
    def ret_int_cast(self, cmdline):
        return int(self.ret_float(cmdline))

    def ret_str(self, cmdline):
        out = self.ret_raw(cmdline=cmdline).decode("utf-8")
        assert out.startswith("'") and out.endswith("'"), f"Output does not seem to be a string: `{out}`"
        return out[1:-1]
    
    def ret_json(self, cmdline):
        return json.loads(self.ret_raw(cmdline)[1:-1])
    
    def __del__(self):
        self.nodejs.sendline("process.exit()")
