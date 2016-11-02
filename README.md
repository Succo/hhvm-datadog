# A custom check for the dd agent to monitor hhvm the PHP JIT interpreter from facebook

To add this to your agent just drop hhvm.py in `checks.d` folder and hhvm.yaml into `conf.d`inside your datadog agent config folder.
You'll need to update the yaml file by updating the url and the password if necessary (see [hhvm-server](https://docs.hhvm.com/hhvm/advanced-usage/admin-server) for the hhvm config).

This is not production tested.
For now it only monitors the result from `/memory.json` and `/cheack-healt`.

Here are an examples return value:

```
{
  "Success": 1, 
  "Memory": {
    "Breakdown": {
      "Unknown": 580800246, 
      "Code": {
        "Details": {
          "Bytes": 69296128
        }
      }, 
      "TC/Jit": {
        "Bytes": 213909504, 
        "Details": {
          "code.main": {
            "Used": 34988, 
            "Capacity": 62914560
          },
          "Total Used": 636020, 
          "Total Capacity": 213909504, 
          "code.hot": {
            "Used": 0, 
            "Capacity": 0
          }, 
          "code.cold": {
            "Used": 50129, 
            "Capacity": 25165824
          }, 
          "code.prof": {
            "Used": 292603, 
            "Capacity": 67108864
          }, 
          "data": {
            "Used": 216, 
            "Capacity": 16777216
          }, 
          "code.frozen": {
            "Used": 258084, 
            "Capacity": 41943040
          }
        }
      }, 
      "Static Strings": {
        "Bytes": 2277642, 
        "Details": {
          "Count": 25204
        }
      }
    }, 
    "Process Stats (bytes)": {
      "Shared": 129179648, 
      "VmSize": 866283520, 
      "VmRss": 175067136, 
      "Data": 490242048, 
      "Text(Code)": 69296128
    }
  }
}

{
 "load":0
, "queued":0
, "hhbc-roarena-capac":0
, "tc-hotsize":0
, "tc-size":99282
, "tc-profsize":1266360
, "tc-coldsize":187629
, "tc-frozensize":1064636
, "rds":23600
, "rds-local":88758
, "rds-persistent":63152
, "catch-traces":25565
, "fixups":22256
, "units":82
, "funcs":7592
, "request-count":249
, "single-jit-requests":20
, "prof-funcs":562
, "prof-bc":165213
, "opt-funcs":0
}
```

It would be great to add the other metrics, and also to avoid craching if the result if not formed exactly as in my example, as it is not really documented.
