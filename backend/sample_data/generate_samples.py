"""
Generates a folder of plain-text sample "invoices" you can upload to the
API to see extraction + anomaly detection in action, without needing real
scanned documents. Includes a few intentional duplicates, an outlier, and
a policy violation so the demo has something interesting to show.

Run with: python generate_samples.py
"""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLES = [
    ("invoice_001.txt", """
        Vendor: Acme Office Supplies Pvt Ltd
        Invoice Number: INV-2001
        Date: 05/01/2026
        Category: Office Supplies
        Description: Printer paper, pens, folders
        Total: INR 4,500.00
    """),
    ("invoice_002.txt", """
        Vendor: Skyline Travels
        Invoice Number: INV-2002
        Date: 06/01/2026
        Description: Flight booking - Bangalore to Mumbai
        Total: INR 12,300.00
    """),
    ("invoice_003.txt", """
        Vendor: Skyline Travels
        Invoice Number: INV-2003
        Date: 06/01/2026
        Description: Flight booking - Bangalore to Mumbai (duplicate submission)
        Total: INR 12,300.00
    """),  # intentional duplicate of #2
    ("invoice_004.txt", """
        Vendor: CloudSoft Technologies
        Invoice Number: INV-2004
        Date: 10/01/2026
        Description: Annual software subscription license
        Total: INR 85,000.00
    """),
    ("invoice_005.txt", """
        Vendor: CloudSoft Technologies
        Invoice Number: INV-2005
        Date: 20/01/2026
        Description: Additional software license seats
        Total: INR 940,000.00
    """),  # statistical + policy outlier vs same vendor's usual spend
    ("invoice_006.txt", """
        Vendor: Café Bloom
        Invoice Number: INV-2006
        Date: 12/01/2026
        Description: Team lunch meeting
        Total: INR 2,100.00
    """),
    ("invoice_007.txt", """
        Vendor: Café Bloom
        Invoice Number: INV-2007
        Date: 15/01/2026
        Description: Client dinner
        Total: INR 9,800.00
    """),  # policy violation: exceeds meals category limit
    ("invoice_008.txt", """
        Vendor: Precision Consulting Group
        Invoice Number: INV-2008
        Date: 18/01/2026
        Description: Q1 advisory services
        Total: INR 210,000.00
    """),
]

if __name__ == "__main__":
    for filename, content in SAMPLES:
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            f.write(content.strip())
    print(f"Generated {len(SAMPLES)} sample files in {OUTPUT_DIR}")
