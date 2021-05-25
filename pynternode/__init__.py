import pexpect
import json
import re
import time

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
    
    def _wait_finish_strict(self):
        index = self.nodejs.expect_exact(["Thrown:", "async>"])
        if index == 0:
            raise RuntimeError("Exception in JS")
        while True:
            try:
                out = self.nodejs.read_nonblocking(timeout=0.5)
            except:
                break 

    def _wait_finish(self):
        print("WAIT FINISH")
        out = b""
        ts = time.time()
        while True:
            try:
                out += self.nodejs.read_nonblocking(timeout=0.2)
                if b"async>" in out:
                    break
            except:
                time.sleep(0.2) 
                if time.time() - ts > 0.5:
                    print("WAIT IFNISH TIMEIOUYT")
                    break
        out = ansi_escape_8bit.sub(b'', out).strip().decode("utf-8")
        if "Thrown:" in out:
            raise RuntimeError(f"Exception in JS: {out}")
        print("WAIT FINISH OUT IS:\n", out)
        time.sleep(0.05)
        return out
    
    def exec_logall(self, cmdline):
        print("=====================")
        print("EXEC_LOGALL Sending line to nodejs:", cmdline)
        self.nodejs.sendline("")
        time.sleep(0.05)
        self._wait_finish()
        time.sleep(0.05)
        self.nodejs.sendline(cmdline)
        out = b""
        while True:
            try:
                out += self.nodejs.read_nonblocking(timeout=0.5)
            except:
                break
        out = ansi_escape_8bit.sub(b'', out).strip()
        print(out.decode("utf-8"))
    
    def execl(self, cmdline):
        print("=====================")
        print("Sending line to nodejs:", cmdline)
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        time.sleep(0.01)
        self.nodejs.sendline(cmdline.encode("utf-8"))
        time.sleep(0.05)
        # out = self.nodejs.readline()
        # out = ansi_escape_8bit.sub(b'', out).strip()
        # print(out)
    
    def run(self, cmdline):
        print("Running no result")
        self.execl(cmdline)
        self._wait_finish()
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        self.nodejs.sendline("")
        time.sleep(0.01)
        self._wait_finish()
        print("END Running no result")
    
    def ret_raw(self, cmdline):
        self.execl(cmdline)
        out = self.nodejs.readline()
        while out.startswith(b" ") or out.startswith(b'(node:') or b"async>" in out:
            print("Raw ret (wait for more)", out)
            out = self.nodejs.readline()
        if cmdline in out.decode("utf-8"):
            out = self.nodejs.readline()
        if out == b'Thrown:\r\n':
            # all_ret = self._wait_finish()
            all_ret = out
            #print(out)
            old_timeout = self.nodejs.timeout
            self.nodejs.timeout = 1
            try:
                while out:
                    out = self.nodejs.readline()
                    print(out)
                    all_ret += out
            except:
                pass
            self.nodejs.timeout = old_timeout
            raise RuntimeError(f"JS Exception: Thrown:\n{all_ret}")
        out_fix = ansi_escape_8bit.sub(b'', out).strip()
        print("Final return(next is wait finish)>>>", out_fix)
        self._wait_finish()
        print("Final return>>>", out)
        return out_fix

    def ret_int(self, cmdline):
        out = "<incomplete>"
        try:
            out = self.ret_raw(cmdline)
            return int(out)
        except ValueError:
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
