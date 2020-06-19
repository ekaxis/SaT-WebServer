import logging


class Analyze:
    def __init__(self, alerts=None):
        if alerts is None: alerts = {}
        self.__alerts = alerts

    def __len__(self):
        if self.__alerts is not None:
            return len(self.__alerts)
        return 0

    def __getitem__(self, inx):
        try:
            alert = self.__alerts[inx]
            return alert
        except Exception as e:
            logging.warning(' - error class analyze: %s' % e)
            return None

    def get(self, index):
        return self.__getitem__(index)

    def __add__(self, other):
        self.__alerts[len(self)] = other

    def add(self, other):
        self.__add__(other)

if __name__ == '__main__':
    pass
