# ffurf

Pronounced "furv" after the Welsh word for "form" or "shape" (and short for the much longer and harder to say Welsh word for configuration), `ffurf` is a very lightweight Python library for defining and loading simple configurations.
`ffurf` is yet another configuration parser and is just a cleaned up version of the code I write over and over for small projects. There is almost certainly [a bigger and better library](http://dynaconf.com/) but I make `ffurf` available in the hope it might be useful to someone who wants a small and non-intrusive way to handle very simple configurations.

## How do I use it?

### Define a configuration

Initialise a `FfurfConfig` and add the settings you want it to hold:

```python
from ffurf import FfurfConfig

ffurf = FfurfConfig()
ffurf.add_config_key("my_first_key")
ffurf.add_config_key("my_optional_key", optional=True)
ffurf.add_config_key("my_almost_secret_key", key_type=int, partial_secret=4)
ffurf.add_config_key("my_secret_int", key_type=int, secret=True)
```

You can specify a key_type which will be used to coerce any potential value for
the key to the right type when stored.

Keys can be marked as secret, which means that printing or `rich` printing the
configuration will hide them. Keys can also be marked as partial_secret, which
will print the last N characters when printing or `rich` printing.

### Export the configuration template

Return a string that can be written out to a TOML file:

```python
ffurf.to_toml()
```

Return a string that can be written out to a dotenv file:

``python
ffurf.to_env()
```


### Fill the configuration

Load a configuration from your environment, disk, or any dict:

```python
os.environ["MY_FIRST_KEY"] = "hoot"
ffurf.from_env()
```

```python
ffurf.from_toml("my_configuration.toml")
```

```python
d = {"my_first_key": "hoot"}
ffurf.from_dict(d)
```

You can also set values in the configuration directly if you'd like:

```python
ffurf["my_first_key"] = "hoot"
```

Values can also be set with the `set_config_key` helper:

```python
ffurf.set_config_key("my_first_key", "hoothoot", source="README example")
```

No matter how you set a key, setting a non-optional key to `None` will
raise a `TypeError`. Setting a key that is not in the configuration will
raise a `KeyError`.

### Validate the configuration

```python
ffurf.is_valid()
```

Currently this will only check that all required keys have been filled.

### Access the configuration

You can access the configuration like a dictionary (because it is):

```python
ffurf["my_first_key"]
```

If you think you might want to fetch a key that might not be in the configuration,
or might be unset, use `get`; like a dictionary:

```python
ffurf.get("my_first_key", default=None)
```

The default will be applied in the case where the key is not in the configuration,
or when the key is in the configuration but has not been set. The latter is useful
when printing out empty configurations.

You can also get "cleaned" versions of the values which will mask out secrets
and partial secrets:

```python
ffurf.get_clean("my_secret_key")
```

### Print the configuration

Print the configuration as a secret-sanitised dict:

```python
print(ffurf)
```

Print the configuration into a pretty, secret-sanitised table:

```python
from rich import print as rich_print
rich_print(ffurf)
```
