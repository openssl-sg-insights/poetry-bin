from importlib.metadata import EntryPoint

from .base import ComponentBuilder


class SeederSelector(ComponentBuilder):
    _ENTRY_POINTS = {
        "virtualenv.seed": [
            EntryPoint(
                name=name,
                value=f"virtualenv.seed.embed.{dst}",
                group="virtualenv.seed"
            ) for name, dst in [
                ("pip", "pip_invoke:PipInvoke"),
                ("app-data", "via_app_data.via_app_data:FromAppData")
            ]
        ]
    }

    def __init__(self, interpreter, parser):
        possible = self.options("virtualenv.seed")
        super().__init__(interpreter, parser, "seeder", possible)

    def add_selector_arg_parse(self, name, choices):
        self.parser.add_argument(
            f"--{name}",
            choices=choices,
            default=self._get_default(),
            required=False,
            help="seed packages install method",
        )
        self.parser.add_argument(
            "--no-seed",
            "--without-pip",
            help="do not install seed packages",
            action="store_true",
            dest="no_seed",
        )

    @staticmethod
    def _get_default():
        return "app-data"

    def handle_selected_arg_parse(self, options):
        return super().handle_selected_arg_parse(options)

    def create(self, options):
        return self._impl_class(options)


__all__ = [
    "SeederSelector",
]
