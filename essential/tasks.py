from write_up.models import WriteUp


def validate():
    """ Plugin ML model to validate engagement on a writeup here """
    return True


def distribute_earnings():
    write_ups = WriteUp.objects.filter()


class ValidateWriteUpEngagement(object):
    @staticmethod
    def get_write_ups():
        return WriteUp.objects.filter()

    def __init__(self):
        write_ups = self.get_write_ups()
