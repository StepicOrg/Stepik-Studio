import warnings
import os


# TODO: Replace no_letters_or_digits to only allowed characters
def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~& '
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)


def deprecated(func):
    def new_func(*args, **kwargs):
        warnings.warn('Call to deprecated function {}.'.format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def file_exist(path):
    return os.path.exists(path)
