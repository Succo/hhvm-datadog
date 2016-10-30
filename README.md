# A custom check for the dd agent to monitor hhvm the PHP JIT interpreter from facebook

To add this to your agent just drop hhvm.py in `checks.d` folder and hhvm.yaml into `conf.d`inside your datadog agent config folder.
You'll need to update the yaml file by updating the url and the password if necessary (see [hhvm-server](https://docs.hhvm.com/hhvm/advanced-usage/admin-server) for the hhvm config.

This is not production tested.
For now it only monitors the result from `/memory.json`.

Here's an example return value:

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
```

It would be great to add the other metrics, and fix error handling to not crash on one missing metric (since the precise list is very dependant on the hhvm version).
