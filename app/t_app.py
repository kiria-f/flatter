import asyncio

from core.input_processor import InputProcessor
from pynput.keyboard import Key, KeyCode


async def main():
    print('hewwo')
    async with InputProcessor() as input_processor:
        while key := await input_processor.read_key():
            if isinstance(key, Key):
                print(f'Key: {key}')
            elif isinstance(key, KeyCode):
                print(f'KeyCode: {key.char}')
                if key.char == 'q':
                    break
            else:
                print('Unknown key type')


if __name__ == '__main__':
    asyncio.run(main())
