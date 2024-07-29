import ngrok
from dotenv import load_dotenv, find_dotenv, set_key, get_key


def run():
    load_dotenv(override=True)
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


if __name__ == "__main__":
    run()
