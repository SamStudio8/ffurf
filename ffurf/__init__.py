__VERSION__ = "0.0.2"

import toml
import json
import sys
import os

from inspect import currentframe, getframeinfo

from rich.table import Table


class FfurfConfig:
    def __init__(self):
        self.config = {}
        self.config_keys = set([])

    def add_config_key(
        self,
        key,
        key_type=str,
        default_value=None,
        secret=False,
        partial_secret=None,
        optional=False,
    ):

        self.config[key] = {
            "name": key,
            "type": key_type,
            "value": key_type(default_value) if default_value else None,
            "source": "ffurf:default" if default_value else None,
            "secret": secret,
            "partial_secret": partial_secret if not secret else None,
            "optional": optional,
        }
        self.config_keys.add(key)

    def __repr__(self):
        # TODO String for making the Ffurf class
        return str({k: self.get_clean(k) for k in self})

    def __str__(self):
        return str({k: self.get_clean(k) for k in self})

    def __rich_console__(self, console, options):
        # Print as a nice table
        table = Table(title="Configuration", show_lines=False)
        table.add_column("Key")
        table.add_column("Value")
        table.add_column("Source")

        for k in self:
            table.add_row(k, self.get_clean(k), self.get_source(k))

        yield table

    def __getitem__(self, k):
        if k not in self.config_keys:
            raise KeyError(k)
        return self.get(k)

    def __setitem__(self, k, v):
        frameinfo = getframeinfo(currentframe().f_back)
        source = "src:%s.%d" % (frameinfo.filename, frameinfo.lineno)
        return self.set_config_key(k, v, source)

    def __iter__(self):
        for k in sorted(self.config_keys):
            yield k

    def __len__(self):
        return len(self.config_keys)

    def __contains__(self, k):
        return k in self.config_keys

    def get(self, k, default=None):
        v = self.config.get(k, {"value": default})["value"]
        if v is None:
            return default
        return v

    def get_keyconf(self, k):
        if k not in self.config_keys:
            raise KeyError(k)
        return self.config[k]

    def get_source(self, k):
        if k not in self.config_keys:
            raise KeyError(k)
        return str(self.config[k]["source"])

    def get_clean(self, k):
        if k not in self.config_keys:
            raise KeyError(k)

        # TODO test
        if self[k] is None:
            return ""

        if self.config[k]["secret"]:
            return "********"
        elif self.config[k]["partial_secret"]:
            return "********" + self[k][-self.config[k]["partial_secret"] :]
        return str(self[k])

    def is_valid(self):
        for k, v in self.config.items():
            if not v["value"] and not v["optional"]:
                return False
        return True

    def set_config_key(self, key, value, source=None):
        if not source:
            frameinfo = getframeinfo(currentframe().f_back)
            source = "src:%s.%d" % (frameinfo.filename, frameinfo.lineno)

        if key not in self.config:
            raise KeyError(key)

        if value is None:
            if not self.config[key]["optional"]:
                raise Exception("%s cannot be null" % key)
        else:
            try:
                key_type = self.config[key]["type"]
                value = key_type(value)
            except:
                raise TypeError(key)

        self.config[key].update(
            {
                "value": value,
                "source": source,
            }
        )

    def from_dict(self, d, source="src", profile=None):
        frameinfo = getframeinfo(currentframe().f_back)
        source = "src:%s.%d" % (frameinfo.filename, frameinfo.lineno)
        return self._from_dict(d, source=source, profile=profile)

    def _from_dict(self, d, source="src", profile=None):

        for k in self.config:

            # Try and get key from the root
            if k in d:
                self.set_config_key(k, d[k], "%s" % source)

            # Load key from default config
            if k in d.get("default", {}):
                self.set_config_key(k, d["default"][k], "%s:default" % source)

            if profile:
                # Allow profile to override top level config
                if k in d.get("profile", {}).get(profile):
                    self.set_config_key(
                        k,
                        d["profile"][profile][k],
                        "%s:profile.%s" % (source, profile),
                    )

    @staticmethod
    def key_to_envkey(k):
        return "".join([ch if ch.isalnum() else "_" for ch in k]).upper()

    def from_env(self):
        for k in self.config:
            env_k = self.key_to_envkey(k)
            env_v = os.getenv(env_k)
            if env_v:
                self._from_dict({k: env_v}, "env:%s" % env_k)

    # TODO test
    def to_toml(self, default=""):
        return toml.dumps({k: self.get(k, default="") for k in self})

    # TODO test
    def to_json(self, default=""):
        return json.dumps({k: self.get(k, default="") for k in self})

    # TODO test
    def to_env(self, default=""):
        env_lines = []
        for k in self:
            env_lines.append('%s="%s"' % (self.key_to_envkey(k), str(self[k])))
        return "\n".join(env_lines)

    # TODO test
    def to_dictstr(self, default=""):
        return str({k: self.get(k, default="") for k in self})

    def from_toml(self, toml_fp, profile=None):
        if not os.path.exists(toml_fp):
            sys.stderr.write("Could not open toml: %s\n" % toml_fp)
            raise OSError()

        toml_config = toml.load(toml_fp)
        self._from_dict(toml_config, source=toml_fp)

    # TODO test
    def from_json(self, json_fp, profile=None):
        if not os.path.exists(json_fp):
            sys.stderr.write("Could not open json: %s\n" % json_fp)
            raise OSError()

        with open(json_fp) as json_fh:
            json_config = json.load(json_fh)
        self._from_dict(json_config, source=json_fp)
