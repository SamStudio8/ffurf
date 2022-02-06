# ffurf

Pronounced "furv" after the Welsh word for "form" or "shape" (and short for the much longer and harder to say Welsh word for configuration), `ffurf` is a very lightweight Python library for defining and loading simple configurations.
`ffurf` is yet another configuration parser and is just a cleaned up version of the code I write over and over for small projects. There is almost certainly [a bigger and better library](http://dynaconf.com/) but I make `ffurf` available in the hope it might be useful to someone who wants a small and non-intrusive way to handle very simple configurations.

## How do I use it?

### Define a configuration

Initialise a `FfurfConfig` and add the settings you want it to hold:

```
from ffurf import FfurfConfig

ffurf = FfurfConfig()
ffurf.add_config_key("my_first_key")
ffurf.add_config_key("my_optional_key", optional=True)
ffurf.add_config_key("my_almost_secret_key", key_type=int, partial_secret=4)
ffurf.add_config_key("my_secret_int", key_type=int, secret=True)
```

Keys can be marked as secret, which means that printing or `rich` printing the
configuration will hide them. Keys can also be marked as partial_secret, which
will print the last N characters when printing or `rich` printing.

### Fill the configuration

Load a configuration from your environment and/or disk:

```
ffurf.from_env()
```

```
ffurf.from_toml("my_configuration.toml")
```

### Validate the configuration

```
ffurf.is_valid()
```
