from babel.util import distinct

# Monkeypatch to work around http://babel.edgewall.org/ticket/228
def Message__init__(self, id, string=u'', locations=(), flags=(), auto_comments=(),
             user_comments=(), previous_id=(), lineno=None):
    """Create the message object.

    :param id: the message ID, or a ``(singular, plural)`` tuple for
               pluralizable messages
    :param string: the translated message string, or a
                   ``(singular, plural)`` tuple for pluralizable messages
    :param locations: a sequence of ``(filenname, lineno)`` tuples
    :param flags: a set or sequence of flags
    :param auto_comments: a sequence of automatic comments for the message
    :param user_comments: a sequence of user comments for the message
    :param previous_id: the previous message ID, or a ``(singular, plural)``
                        tuple for pluralizable messages
    :param lineno: the line number on which the msgid line was found in the
                   PO file, if any
    """
    self.id = id #: The message ID
    if not string and self.pluralizable:
        string = (u'', u'')
    self.string = string #: The message translation
    self.locations = list(distinct(locations))
    self.flags = set(flags)
    if id and self.python_format:
        self.flags.add('python-format')
    else:
        self.flags.discard('python-format')
    self.auto_comments = list(auto_comments)
    self.user_comments = list(user_comments)
    if isinstance(previous_id, basestring):
        self.previous_id = [previous_id]
    else:
        self.previous_id = list(previous_id)
    self.lineno = lineno


applied = False

def applyPatches():
    global applied

    if not applied:
        from babel.messages.catalog import Message
        Message.__init__=Message__init__
        applied=True
