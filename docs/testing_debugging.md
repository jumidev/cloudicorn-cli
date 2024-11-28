# Testing and debugging notes

Running cloudicorn directly from source

```
cd cli
python3 -m cloudicorn.cloudicorn [ARGS]
```

## debugging

Example debuggy call

```  
python3 -m debugpy --listen 5678  --wait-for-client  -m cloudicorn.cloudicorn
```

Launch.json vscode config that will connect to above debugpy instance

https://code.visualstudio.com/docs/python/debugging#_command-line-debugging

```
{
    "name": "Python debugpy",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    }
},
```

# running tests

By default tests will be run against terraform.  To install terraform, run

```
cloudicorn_setup --install
```

To run the tests against opentofu

```
cd tests
make enable_opentofu
cloudicorn_setup --install
```

Once opentofu or terraform is installed, tests can be run

```
cd tests
make test # runs all tests, internet connection required, no cloud credentials required
```

To run specific tests:

```
export TEST_FILTER=001
make test_TEST_FILTER
```

