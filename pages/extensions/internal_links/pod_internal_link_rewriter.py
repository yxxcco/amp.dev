import os
import re
import traceback
from grow.pods.pods import Pod
from grow.documents.document import Document

# find all <a href without a : in the link and not ending with /
LINK_PATTERN = re.compile(r'<a\s+(?:[^>]+\s)?href\s*=\s*"((?:[^"#?](?!:))*?[^"/])((?:\?[^"]*)?(?:#[^"]*)?)"',
                          re.IGNORECASE)


class PodInternalLinkRewriter(object):

  pod = None  # type: Pod

  def __init__(self, doc):
    """
    :type doc: Document
    """
    self.doc = doc
    self.pod = doc.pod

  def rewrite_pod_internal_links(self, content):
    """
    :type content: str
    """
    try:
      pos = 0
      result = ''

      match = LINK_PATTERN.search(content)
      while match:
        result = result + content[pos: match.start(1)]

        # group 1 is the link, group 2 is the optional query and anchor part
        result = result + self.rewrite_link(match.group(1), match.group(2))
        result = result + content[match.end(2):match.end(0)]

        pos = match.end(0)
        match = LINK_PATTERN.search(content, match.end(0))

      result = result + content[pos: ]
      return result

    except Exception as err:
      stack = traceback.format_exc()
      self.pod.logger.error('Error while trying to rewrite internal links for doc {}: {}\n{}'
                            .format(self.doc.pod_path, err, stack))
      return content

  def rewrite_link(self, internal_link, query_and_anchor):
    """
    :type query_and_anchor: str
    :type internal_link: str
    """
    try:
      internal_path = internal_link

      if not internal_path.startswith('/'):
        internal_path = os.path.abspath(os.path.join(
          PodInternalLinkRewriter.get_folder(self.doc.pod_path), internal_path))

      target_doc = self.pod.get_doc(internal_path, self.doc.locale)

      if not target_doc.exists:
        return internal_link

      result = target_doc.url.path

    except Exception as err:
      self.pod.logger.warn('Unable to rewrite internal link {} in {}'.format(internal_link, self.doc.pod_path))
      result = internal_link

    if query_and_anchor:
      result = result + query_and_anchor
    return result


  @staticmethod
  def get_folder(path):
    """
    :type path: str
    """
    idx = path.rfind('/')
    if idx < 0:
      return path
    return path[:idx]
