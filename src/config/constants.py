import os

# Data directories
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
FEEDBACK_DIR = os.path.join(DATA_DIR, "feedback")
INCOMING_DIR = os.path.join(DATA_DIR, "incoming")
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")

# Snapshot file paths
STOCK_SNAPSHOT_PATH = os.path.join(RESOURCES_DIR, "last_stock.csv")
SALES_SNAPSHOT_PATH = os.path.join(RESOURCES_DIR, "sales_snapshot.csv")
METRIC_SNAPSHOT_DIR = os.path.join(RESOURCES_DIR, "metric_snapshots")

# Error log path
ERROR_LOG_FILE = os.path.join(DATA_DIR, "error_logs.json")

# Persistence
STATE_FILE = os.path.join(DATA_DIR, "session_state.json")

# Common category options for filter UI
COMMON_CATS = [
    "Belt",
    "Boxer",
    "Bundles",
    "FS Shirt",
    "  \u21b3 Denim Shirt",
    "  \u21b3 FS Casual Shirt",
    "  \u21b3 Flannel Shirt",
    "  \u21b3 Kaftan Shirt",
    "  \u21b3 Oxford Shirt",
    "HS Shirt",
    "  \u21b3 Contrast Shirt",
    "  \u21b3 HS Casual Shirt",
    "Jeans",
    "  \u21b3 Regular Fit Jeans",
    "  \u21b3 Slim Fit Jeans",
    "  \u21b3 Straight Fit Jeans",
    "Leather Bag",
    "Mask",
    "Others",
    "Panjabi",
    "  \u21b3 Embroidered Cotton Panjabi",
    "Polo Shirt",
    "Sweatshirt",
    "  \u21b3 Cotton Terry Sweatshirt",
    "  \u21b3 French Terry Sweatshirt",
    "T-Shirt",
    "  \u21b3 Active Wear",
    "  \u21b3 Drop Shoulder",
    "  \u21b3 FS-T-Shirt",
    "  \u21b3 HS T-Shirt",
    "  \u21b3 Jersy",
    "  \u21b3 Tank Top",
    "Trousers",
    "  \u21b3 Joggers",
    "  \u21b3 Regular Fit Trousers",
    "Turtle-Neck",
    "Twill",
    "  \u21b3 Twill Five Pockets",
    "  \u21b3 Twill Joggers",
    "  \u21b3 Twill Chino",
    "Wallet",
    "  \u21b3 Bifold Wallet",
    "  \u21b3 Card Holder",
    "  \u21b3 Long Wallet",
    "  \u21b3 Passport Holder",
    "  \u21b3 Trifold Wallet",
    "Water Bottle"
]

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FEEDBACK_DIR, exist_ok=True)
os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(RESOURCES_DIR, exist_ok=True)
os.makedirs(METRIC_SNAPSHOT_DIR, exist_ok=True)
