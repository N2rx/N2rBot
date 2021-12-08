import base64
from datetime import datetime
import hashlib
import json
import sys
import platform
import random
import string
import colorama


from time import sleep
from Crypto import Random
from Crypto.Cipher import AES
from colorama import Fore, init

import settings
from webhook import DiscordEmbed, DiscordWebhook


text = """
        $$\   $$\        $$$$$$\        $$$$$$$\  
        $$$\  $$ |      $$  __$$\       $$  __$$\ 
        $$$$\ $$ |      \__/  $$ |      $$ |  $$ |
        $$ $$\$$ |       $$$$$$  |      $$$$$$$  |
        $$ \$$$$ |      $$  ____/       $$  __$$< 
        $$ |\$$$ |      $$ |            $$ |  $$ |
        $$ | \$$ |      $$$$$$$$\       $$ |  $$ |
        \__|  \__|      \________|      \__|  \__|
                                          
    """


colors = list(vars(colorama.Fore).values())
colored_chars = [random.choice(colors) + char for char in text]

colorama.init()
normal_color = Fore.CYAN
white_color = Fore.WHITE



def write_data(path, data):
    with open(path, "w") as file:
        json.dump(data, file)


# TODO: Enable this as an app setting for user to choose their own optional key & regenerate key on the fly button
try:
    with open("./data/vault.json", "r") as file:
        keys = json.load(file)
except FileNotFoundError:
    generateKeySecret = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    write_data("./data/vault.json", [{"generated_key_secret": generateKeySecret}])
    with open("./data/vault.json", "r") as file:
        keys = json.load(file)

e_key = keys[0]['generated_key_secret'].encode()
BLOCK_SIZE = 16
if platform.system() == "Windows":
    init(convert=True)
else:
    init()



print(''.join(colored_chars))

print("Discord N2r#6089")


class BirdLogger:
    @staticmethod
    def ts():
        return str(datetime.now())[:-7]

    def normal(self, task_id, account, msg):
        print(normal_color + "[{}][TASK {}][ACCOUNT {}] {}".format(self.ts(), task_id, account, msg))

    def alt(self, task_id, msg):
        print(Fore.MAGENTA + "[{}][TASK {}] {}".format(self.ts(), task_id, msg))

    def carted(self, task_id, account, msg):
        print(Fore.YELLOW + "[{}][TASK {}][ACCOUNT {}] {}".format(self.ts(), task_id, account, msg))

    def error(self, task_id, msg):
        print(Fore.RED + "[{}][TASK {}] {}".format(self.ts(), task_id, msg))

    def success(self, task_id, account, msg):
        print(Fore.GREEN + "[{}][TASK {}][ACCOUNT {}] {}".format(self.ts(), task_id, account, msg))


class Encryption:
    def encrypt(self, msg):
        IV = Random.new().read(BLOCK_SIZE)
        aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
        return base64.b64encode(IV + aes.encrypt(msg.encode("utf-8")))

    def decrypt(self, msg):
        msg = base64.b64decode(msg)
        IV = msg[:BLOCK_SIZE]
        aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
        return aes.decrypt(msg[BLOCK_SIZE:])

    @staticmethod
    def trans(key):
        return hashlib.md5(key).digest()


def return_data(path):
    try:
        with open(path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        write_data(path, [])
        with open(path, "r") as file:
            data = json.load(file)
        return data


def validate_data(test_data, control_data):
    return test_data.keys() == control_data.keys()


def data_exists(path):
    try:
        open(path, "r")
        return True
    except FileNotFoundError:
        return False


def get_profile(profile_name):
    profiles = return_data("./data/profiles.json")
    for p in profiles:
        if p["profile_name"] == profile_name:
            try:
                p["card_number"] = (Encryption().decrypt(p["card_number"].encode("utf-8"))).decode("utf-8")
            except ValueError:
                pass
            return p
    return None

def get_account(account_name):
    accounts = return_data("./data/accounts.json")
    for p in accounts:
        if p["account_name"] == account_name:
            try:
                p["account_pass"] = (Encryption().decrypt(p["account_pass"].encode("utf-8"))).decode("utf-8")
            except ValueError:
                pass
            return p
    return None


def get_proxy(list_name):
    if list_name == "Proxy List" or list_name == "None":
        return False
    proxies = return_data("./data/proxies.json")
    for proxy_list in proxies:
        if proxy_list["list_name"] == list_name:
            return format_proxy(random.choice(proxy_list["proxies"].splitlines()))
    return None


def format_proxy(proxy):
    try:
        proxy_parts = proxy.split(":")
        ip, port, user, passw = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
        return {
            "http": "http://{}:{}@{}:{}".format(user, passw, ip, port),
            "https": "https://{}:{}@{}:{}".format(user, passw, ip, port)
        }
    except IndexError:
        return {"http": "http://" + proxy, "https": "https://" + proxy}


def send_webhook(webhook_type, site, profile, product, account, image_url):
    if settings.webhook != "":
        webhook = DiscordWebhook(url=settings.webhook, username="N2r Bot",
                                 avatar_url="https://i.imgur.com/VGVWdjY.png")
        if webhook_type == "OP":
            if not settings.webhook_on_order:
                return
            embed = DiscordEmbed(title="Successful Checkout", color=0x1eff00)
        elif webhook_type == "B":
            if not settings.webhook_on_browser:
                return
            embed = DiscordEmbed(title="Complete Order in Browser", color=0xf2a689)
        elif webhook_type == "PF":
            if not settings.webhook_on_failed:
                return
            embed = DiscordEmbed(title="Payment Failed", color=0xfc5151)
        embed.set_footer(text="Via N2r Bot", icon_url="https://i.imgur.com/VGVWdjY.png")
        embed.add_embed_field(name="Site", value=site, inline=True)
        embed.add_embed_field(name="Profile", value=profile, inline=True)
        embed.add_embed_field(name="Product", value=product, inline=True)
        embed.add_embed_field(name="Account", value=account, inline=True)
        embed.set_thumbnail(url=image_url)
        webhook.add_embed(embed)
        try:
            webhook.execute()
        except:
            pass


def random_delay(delay, start, stop):
    """
    Returns the delay argument combined with a random number between start
    and stop divided by 1000.
    """
    return delay + (random.randint(int(start), int(stop)) / 1000)


def create_msg(msg, status):
    return {"msg": msg, "status": status}
