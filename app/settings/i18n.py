import gettext

def get_translations(language='en'):
    language_translations = gettext.translation('base', localedir='translations', languages=[language], fallback=True)
    language_translations.install()
    _ = language_translations.gettext
    return _

