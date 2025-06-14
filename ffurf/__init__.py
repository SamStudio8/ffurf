__VERSION__ = "0.1.5"

import argparse
import toml
import json
import sys
import os

from inspect import currentframe, getframeinfo


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
            "value": key_type(default_value) if default_value is not None else None,
            "source": "ffurf:default" if default_value is not None else None,
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

    # TODO test
    def __rich_console__(self, console, options):
        try:
            from rich.table import Table
        except ImportError:
            raise RuntimeError("Optional dependency 'rich' is required for pretty-printing. Install with: pip install rich")
        # Print as a nice table
        table = Table(title="Configuration", show_lines=False)
        table.add_column("Key")
        table.add_column("Value")
        table.add_column("Source")
        table.add_column("Valid")

        for k in self:

            v = self.get_clean(k)
            source = self.get_source(k)

            if not self.config[k]["optional"] and self[k] is None:
                v = "[b red]--------[/]"
                source = "[b red]unset[/]"
            elif not self.config[k]["optional"] and self[k] == "":
                v = "[b red]--------[/]"
                source = "%s [b red](blank)[/]" % source

            valid = "[green]O[/]" if self.key_is_valid(k) else "[red]X[/]"
            table.add_row(k, v, source, valid)

        yield table

    def print_table(self):
        rows = []
        for k in self:
            v = self.get_clean(k)
            source = self.get_source(k)
            if not self.config[k]["optional"] and self[k] is None:
                v = "--------"
                source = "unset"
            elif not self.config[k]["optional"] and self[k] == "":
                v = "--------"
                source = f"{source} (blank)"
            valid = "O" if self.key_is_valid(k) else "X"
            rows.append((k, v, source, valid))

        headers = ("Key", "Value", "Source", "Valid")

        col_widths = [len(h) for h in headers]
        for row in rows:
            for col, cell in enumerate(row):
                l = len(str(cell))
                if l > col_widths[col]:
                    col_widths[col] = l

        header_row = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        print(header_row.strip())
        print("  ".join("=" * col_widths[i] for i in range(len(headers))))
        for row in rows:
            cells = [str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)]
            print("  ".join(cells).strip())

    def __getitem__(self, k):
        if k not in self.config_keys:
            raise KeyError(k)
        return self.get(k)

    def __setitem__(self, k, v):
        frameinfo = getframeinfo(currentframe().f_back)
        source = self.frame_to_source(frameinfo)
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

        if self[k] is None:
            return ""

        if self.config[k]["secret"]:
            return "********"
        elif self.config[k]["partial_secret"]:
            return "********" + self[k][-self.config[k]["partial_secret"] :]
        return str(self[k])

    def key_is_valid(self, k):
        if k not in self.config_keys:
            raise KeyError(k)
        k, v = k, self.config[k]
        if v["value"] is None and not v["optional"]:
            return False
        if v["value"] == "" and not v["optional"] and v["type"] is str:
            return False
        return True

    def is_valid(self):
        for k, v in self.config.items():
            if not self.key_is_valid(k):
                return False
        return True

    def validate(self):
        if not self.is_valid():
            self.print_table()
            sys.exit(os.EX_CONFIG)

    def set_config_key(self, key, value, source=None, append_source=False):
        if not source:
            frameinfo = getframeinfo(currentframe().f_back)
            source = self.frame_to_source(frameinfo)

        if append_source and self.config[key]["source"] is not None:
            source = "%s,%s" % (self.config[key]["source"], source)

        if key not in self.config:
            raise KeyError(key)

        if value is None:
            if not self.config[key]["optional"]:
                raise TypeError("%s cannot be None" % key)
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

    @staticmethod
    def frame_to_source(frame):
        return "src:%s@L%d" % (frame.filename.rsplit("ocarina/", 1)[-1], frame.lineno)

    def load(self, thing=None, **kwargs):
        if not thing:
            self.from_env(**kwargs)
        elif isinstance(thing, dict):
            self.from_dict(thing, **kwargs)
        elif isinstance(thing, str):
            if thing.endswith("toml"):
                self.from_toml(thing, **kwargs)
            elif thing.endswith("json"):
                self.from_json(thing, **kwargs)
            else:
                raise ValueError("Unknown file config type: %s" % thing)
        else:
            raise TypeError("Could not infer loader for %s" % type(thing))
        return self

    def from_dict(self, d, source="src", profile=None):
        frameinfo = getframeinfo(currentframe().f_back)
        source = self.frame_to_source(frameinfo)
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
                if k in d.get("profile", {}).get(profile, {}):
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

    # TODO test
    def to_groovy(self, default=""):
        head = "params {"
        tail = "}"
        lines = [head]
        for k in self:
            v = self.get(k, default="")
            if type(v) == str:
                if v == "":
                    # empty strings to null
                    v = "null"
                else:
                    v = f'"{v}"'
            elif type(v) == None:
                v = "null"
            elif type(v) == bool:
                if v:
                    v = "true"
                else:
                    v = "false"
            lines.append(f"    {k} = {v}")

        lines.append(tail)
        return '\n'.join(lines)

    # TODO test
    def to_argparse(self, default=""):
        parser = argparse.ArgumentParser(add_help=False)
        for k, v in self.config.items():
            default_str = f" [default: {v['value']}]" if v["value"] is not None else ""
            parser.add_argument(f"--{k}",
                type=v["type"],
                required=not v["optional"] and v["value"] is None,
                default=v["value"],
                help=""+default_str)
        return parser

    def from_toml(self, toml_fp, profile=None):
        if not os.path.exists(toml_fp):
            sys.stderr.write("Could not open toml: %s\n" % toml_fp)
            raise OSError()

        toml_config = toml.load(toml_fp)
        self._from_dict(toml_config, source=toml_fp, profile=profile)

    def from_json(self, json_fp, profile=None):
        if not os.path.exists(json_fp):
            sys.stderr.write("Could not open json: %s\n" % json_fp)
            raise OSError()

        with open(json_fp) as json_fh:
            json_config = json.load(json_fh)
        self._from_dict(json_config, source=json_fp, profile=profile)
