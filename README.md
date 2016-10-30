# A custom check for the dd agent to monitor hhvm the PHP JIT interpreter from facebook

To add this to your agent just drop hhvm.py in `checks.d` folder and hhvm.yaml into `conf.d`inside your datadog agent config folder.
You'll need to update the yaml file by updating the url and the password if necessary (see [hhvm-server](https://docs.hhvm.com/hhvm/advanced-usage/admin-server) for the hhvm config.

This is not production tested.
For now it only monitors the result from `/memory.json`.

It would be great to add the other metrics, and fix error handling to not crash on one missing metric (since the precise list is very dependant on the hhvm version).
