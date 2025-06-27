import re


def _csi(sign: str, *args: int) -> str:
    return f'\033[{";".join(map(str, args)) if args else ""}{sign}'


def _sgr(*args: int) -> str:
    return _csi('m', *args)


_csi_regex = re.compile(r'\033\[(\d+(;\d+)*)?([a-zA-Z])')
_sgr_regex = re.compile(r'\033\[(\d+(;\d+)*)?m')
