import os
import subprocess
from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADDRESS = os.environ.get("ADDRESS") or "0x032558a3801160d4fec8db90a143e225534a3a0de2fb791b370527b76bf18d16"
SET_ADDRESS = os.environ.get("SET_ADDRESS") or "0x032558a3801160d4fec8db90a143e225534a3a0de2fb791b370527b76bf18d16"
GATEWAY_URL = os.environ.get("GATEWAY_URL") or None
FEEDER_GATEWAY_URL = os.environ.get("FEEDER_GATEWAY_URL") or None

default_args = ["--network", "alpha"]
if (GATEWAY_URL is not None):
    default_args = [
        "--gateway_url", GATEWAY_URL,
        "--feeder_gateway_url", FEEDER_GATEWAY_URL
    ]

print(ADDRESS)
print(SET_ADDRESS)

def get_command(invoke, funcname, inputs, addr = ADDRESS):
    return ["starknet", ("invoke" if invoke else "call"),
            "--address", addr,
            "--abi", "briq_abi.json" if addr == ADDRESS else "set_abi.json",
            "--function", funcname] + (["--inputs"] + inputs if len(inputs) else []) + default_args

def cli_call(command, full_res=False):
    proc = subprocess.run(args=command, capture_output=True)
    val = None
    try:
        if full_res:
            val  = proc.stdout.decode('utf-8')
        else:
            val = proc.stdout.decode('utf-8').split("\n")[0]
    except Exception:
        pass
    if proc.returncode == 0:
        return {
            "code": proc.returncode,
            "value": val
        }
    return {
        "code": proc.returncode,
        "stdout": str(proc.stdout.decode('utf-8')),
        "stderr": str(proc.stderr.decode('utf-8'))
    }

@app.route("/init")
def init():
    cli_call(get_command(True, "initialize", [], SET_ADDRESS))
    return "ok"

@app.route("/call_func/<name>", methods=["GET", "POST"])
def call_func(name):
    try:
        inputs = dispatch_inputs(name, request.get_json()["inputs"])
    except Exception as e:
        return { "error": str(e), "code": 500 }, 500
    print(" ".join(["starknet", get_call_invoke(name),
            "--address", ADDRESS,
            "--abi", "briq_abi.json",
            "--function", name,
            "--inputs"] + inputs + default_args)),
    proc = subprocess.run(args=["starknet", get_call_invoke(name),
            "--address", ADDRESS,
            "--abi", "briq_abi.json",
            "--function", name,
            "--inputs"] + inputs + default_args,
        capture_output=True)
    val = None
    try:
        val = proc.stdout.decode('utf-8').split("\n")[0]
    except Exception:
        pass
    if val is not None:
        return {
            "code": proc.returncode,
            "value": val
        }
    return {
        "code": proc.returncode,
        "stdout": str(proc.stdout.decode('utf-8'))
    }

def dispatch_inputs(name, inputs):
    if name == "balance_of":
        return [str(inputs["owner"])]
    if name == "token_at_index":
        return [str(inputs["owner"]), str(inputs["index"])]
    if name == "owner_of":
        return [str(inputs["token_id"])]
    if name == "mint":
        return [str(inputs["owner"]), str(inputs["token_id"]), str(inputs["material"])]
    if name == "transfer_from":
        return [str(inputs["sender"]), str(inputs["recipient"]), str(inputs["token_id"])]

def get_call_invoke(name):
    if name == "mint" or name == "transfer_from":
        return "invoke"
    return "call"

@app.route("/get_bricks/<owner>", methods=["GET", "POST"])
def get_bricks(owner):
    comm = get_command(False, "balance_of", [str(owner)])
    print(" ".join(comm))
    try:
       balance = int(cli_call(comm)["value"])
    except Exception as e:
        print(e)
        return {
            "error": "Could not get the balance", "code": 500
        }, 500
    runs = balance // 20 + 1
    print(f"runs: {runs}")
    ret = []
    for i in range(0, runs):
        comm = get_command(False, "tokens_at_index", [str(owner), str(i)])
        print(" ".join(comm))
        try:
            bricks = cli_call(comm)["value"].split(" ")
        except Exception:
            return {
                "error": "Error fetching brick data", "code": 500
            }, 500
        for j in range(0, min(balance - i*20, 20)):
            # First token ID, then material, then part-of-set.
            ret.append((hex(int(bricks[j*3])), int(bricks[j*3+1]), int(bricks[j*3+2])))
    return {
        "code": 200,
        "value": ret
    }

import json

@app.route("/store_set", methods=["POST"])
def store_set():
    data = request.get_json()["data"]
    bricks = ["0x123", "0x124", "0x125"]
    
    comm = get_command(False, "get_next_uid", [], SET_ADDRESS)
    print(" ".join(comm))
    token_id = cli_call(comm)["value"]

    comm = get_command(True, "mint_working", ["0x11", str(token_id)], SET_ADDRESS)
    #comm = get_command(True, "mint", [str(len(bricks)+1), "0x11"] + bricks, SET_ADDRESS)
    print(" ".join(comm))
    res = cli_call(comm, full_res=True)["value"].split("\n")[2]
    print(res)

    open(f"temp/{token_id}.json", "w").write(json.dumps(data))

    return {
        "code": 200,
        "value": token_id
    }, 200


@app.route("/store_get/<token_id>", methods=["POST"])
def store_get(token_id):
    comm = get_command(False, "owner_of", [str(token_id)], SET_ADDRESS)
    print(" ".join(comm))
    owner = cli_call(comm)['value']
    print(f"Owner is {owner}")
    if owner == 0:
        return {
            "error": "doesn't exist"
        }, 500

    try:
        data = json.loads(open(f"temp/{token_id}.json", "r").read())
        print(data)
    except Exception as e:
        print(e)
        return {
            "code": 500,
            "error": "File not found"
        }, 500

    return {
        "code": 200,
        "owner": owner,
        "token_id": token_id,
        "data": data
    }, 200
