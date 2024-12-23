import time
import ngrok
import asyncio
from dotenv import load_dotenv, find_dotenv, set_key, get_key


def run():
    load_dotenv(override=True)
    print("Started tunnel")
    dotenv_path = find_dotenv()
    port = get_key(dotenv_path, "PORT")
    domain = get_key(dotenv_path, "DOMAIN")
    if not port:
        raise Exception("PORT is required")
    if not domain:
        raise Exception("DOMAIN is required")
    ngrok.log_level("ERROR")
    listener = ngrok.forward(f"{domain}:{port}", authtoken_from_env=True)
    set_key(dotenv_path, "BOT_WEBHOOK_URL", f"{listener.url()}/bot/webhook")

    try:
        while True:
            time.sleep(1)  # Удерживаем программу активной
    except KeyboardInterrupt:
        print("Shutting down tunnel...")
        asyncio.run(listener.close())


if __name__ == "__main__":
    run()
