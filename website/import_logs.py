# import_logs.py
import sys
import types

# Create fake sklearn modules to satisfy imports
sklearn = types.ModuleType("sklearn")
feature_extraction = types.ModuleType("feature_extraction")
text = types.ModuleType("text")
metrics = types.ModuleType("metrics")
pairwise = types.ModuleType("pairwise")

# Dummy replacements for the parts of sklearn your utils.py imports
class DummyTfidfVectorizer:
    def fit_transform(self, *args, **kwargs):
        return []
    def transform(self, *args, **kwargs):
        return []

def dummy_cosine_similarity(*args, **kwargs):
    return []

# Attach fake contents
text.TfidfVectorizer = DummyTfidfVectorizer
pairwise.cosine_similarity = dummy_cosine_similarity

# Register all mocks
sys.modules["sklearn"] = sklearn
sys.modules["sklearn.feature_extraction"] = feature_extraction
sys.modules["sklearn.feature_extraction.text"] = text
sys.modules["sklearn.metrics"] = metrics
sys.modules["sklearn.metrics.pairwise"] = pairwise
import re
from datetime import datetime
from website import create_app, db
from website.models import Visitor

app = create_app()
app.app_context().push()

LOG_FILE = 'alexandebj.pythonanywhere.com.access.txt'

# regex pattern to extract relevant fields
log_pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+).*?\[(?P<timestamp>[^\]]+)\].*?"GET (?P<url>[^"]+)".*?"(?P<user_agent>[^"]+)"'
)

def classify_user_type(user_agent):
    ua = user_agent.lower()
    if 'facebookexternalhit' in ua or 'fb_iab' in ua:
        return 'facebook'
    elif 'mobile' in ua or 'iphone' in ua or 'android' in ua:
        return 'mobile'
    elif 'ipad' in ua:
        return 'tablet'
    elif 'windows' in ua or 'macintosh' in ua or 'linux' in ua:
        return 'computer'
    else:
        return 'unknown'

with open(LOG_FILE, 'r') as f:
    for line in f:
        m = log_pattern.search(line)
        if not m:
            continue
        
        ip = m.group('ip')
        raw_time = m.group('timestamp')
        user_agent = m.group('user_agent')

        # Parse timestamp like "09/Oct/2025:09:27:44 +0000"
        dt = datetime.strptime(raw_time.split()[0], "%d/%b/%Y:%H:%M:%S")

        visitor = Visitor.query.filter_by(ip=ip).first()
        if visitor:
            visitor.visit_count = (visitor.visit_count or 0) + 1
            if dt > (visitor.last_seen or datetime.min):
                visitor.last_seen = dt
        else:
            new_visitor = Visitor(
                ip=ip,
                last_seen=dt,
                visit_count=1,
                user_type=classify_user_type(user_agent)
            )
            db.session.add(new_visitor)
    db.session.commit()

print("Log import completed successfully.")
