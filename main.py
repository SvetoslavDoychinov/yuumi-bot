from bot.disco_nunu import DiscoNunu
from bot.yuumi import YuumiBot
from common.logger import configure_logger


def main():
    configure_logger()
    bot = YuumiBot()
    # bot = DiscoNunu() if you want Nunu
    bot.main_loop()


if __name__ == '__main__':
    main()
