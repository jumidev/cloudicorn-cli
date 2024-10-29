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

```
cd tests
make test # runs all tests, internet connection required
```

To run specific tests:

```
export TEST_FILTER=001
make test_TEST_FILTER
```

