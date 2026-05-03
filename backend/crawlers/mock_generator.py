"""
Realistic mock data generator for demo purposes.
Generates posts that simulate what would be crawled from Reddit/Twitter.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

MOCK_REDDIT_POSTS = {
    "azithromycin": [
        {
            "id": "r_az_001",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "user_delhi_2024",
            "content": "I've been taking Azithral 500 for 3 days now for throat infection. I started experiencing severe ringing in my ears (tinnitus) yesterday. I have never had this before. My doctor didn't mention this as a side effect. Is this related to the antibiotic? The ringing is constant and quite disturbing.",
            "url": "https://reddit.com/r/AskDocs/comments/az001",
            "posted_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "location": "Delhi",
            "upvotes": 47
        },
        {
            "id": "r_az_002",
            "source": "reddit",
            "subreddit": "r/pharmacy",
            "author": "mumbai_patient_99",
            "content": "I'm on day 4 of azithromycin (Zithromax) for chest infection. I've developed muscle weakness in both my legs. I'm finding it hard to climb stairs. This is very unusual for me. Has anyone else experienced muscle weakness with this antibiotic? I've taken it before and never had this.",
            "url": "https://reddit.com/r/pharmacy/comments/az002",
            "posted_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "location": "Mumbai",
            "upvotes": 23
        },
        {
            "id": "r_az_003",
            "source": "reddit",
            "subreddit": "r/india",
            "author": "banglore_techie",
            "content": "PSA: I had a terrible experience with Azithral last week. I started having severe joint pain in my knees and wrists on day 2. Couldn't walk properly. Had to stop the medication after talking to my doctor. My doctor confirmed it could be drug-related but said it was rare. Just posting so others are aware.",
            "url": "https://reddit.com/r/india/comments/az003",
            "posted_at": (datetime.now() - timedelta(days=8)).isoformat(),
            "location": "Bangalore",
            "upvotes": 89
        },
        {
            "id": "r_az_004",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "hyderabad_user",
            "content": "Day 3 of taking azithromycin for sinusitis. I'm experiencing constant ringing in my ears. It's so loud I can barely sleep. My doctor prescribed Azee 500. Called the clinic and they said to continue but this doesn't feel right. The tinnitus started about 18 hours after my first dose.",
            "url": "https://reddit.com/r/AskDocs/comments/az004",
            "posted_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "location": "Hyderabad",
            "upvotes": 34
        },
        {
            "id": "r_az_005",
            "source": "twitter",
            "subreddit": None,
            "author": "pune_health",
            "content": "I've been prescribed Azithral 500 and I'm having severe tinnitus (ear ringing). The noise is unbearable. I've read online that others are having the same issue but this side effect is NOT listed on the medication leaflet. Has anyone reported this to CDSCO?",
            "url": "https://twitter.com/pune_health/status/az005",
            "posted_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "location": "Pune",
            "upvotes": 156
        },
        {
            "id": "r_az_006",
            "source": "reddit",
            "subreddit": "r/medical",
            "author": "chennai_patient",
            "content": "I had muscle weakness after taking azithromycin. My pharmacist said it's not a listed side effect but I couldn't even lift my arms properly for 2 days. I stopped the medication and it resolved within 48 hours. The weakness was primarily in my upper arms and thighs.",
            "url": "https://reddit.com/r/medical/comments/az006",
            "posted_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "location": "Chennai",
            "upvotes": 67
        },
        {
            "id": "r_az_007",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "kolkata_user_2024",
            "content": "My wife started azithromycin for her ear infection yesterday and she's already complaining of ringing in ears. She is 34 and otherwise healthy. The doctor's prescription doesn't mention tinnitus as a possible side effect. Should we stop the medication?",
            "url": "https://reddit.com/r/AskDocs/comments/az007",
            "posted_at": (datetime.now() - timedelta(days=1, hours=6)).isoformat(),
            "location": "Kolkata",
            "upvotes": 12
        },
        {
            "id": "r_az_008",
            "source": "twitter",
            "subreddit": None,
            "author": "dr_experience_india",
            "content": "Second patient this week reporting tinnitus while on azithromycin course. Both were on Azithral 500. Neither had previous ear issues. The drug label doesn't list this. Anyone else seeing this pattern? Starting to wonder if this is an unreported ADR.",
            "url": "https://twitter.com/dr_experience_india/status/az008",
            "posted_at": (datetime.now() - timedelta(hours=18)).isoformat(),
            "location": "Delhi",
            "upvotes": 234
        },
        {
            "id": "r_az_009",
            "source": "reddit",
            "subreddit": "r/pharmacy",
            "author": "jaipur_pharmacist",
            "content": "I myself experienced severe muscle weakness when I took azithromycin last month. As a pharmacist I was surprised because this isn't a documented side effect in India's CDSCO approved labeling. I had blood tests done and everything was normal once I stopped. The weakness lasted about 3 days.",
            "url": "https://reddit.com/r/pharmacy/comments/az009",
            "posted_at": (datetime.now() - timedelta(days=15)).isoformat(),
            "location": "Jaipur",
            "upvotes": 145
        },
        {
            "id": "r_az_010",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "surat_user",
            "content": "I'm experiencing tinnitus after starting azithromycin treatment. The ringing started on day 2 and has been getting worse. I've taken this antibiotic before without any issues. The current batch is Azee 250mg. My dosage is higher this time. Going to stop and see doctor tomorrow.",
            "url": "https://reddit.com/r/AskDocs/comments/az010",
            "posted_at": (datetime.now() - timedelta(hours=8)).isoformat(),
            "location": "Surat",
            "upvotes": 28
        }
    ],
    "paracetamol": [
        {
            "id": "r_pc_001",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "user_ncr",
            "content": "I've been taking Dolo 650 for fever for 5 days straight. I've developed severe pain in my upper right abdomen. My doctor tested and my liver enzymes are elevated. I was taking the recommended dose but I also had one glass of wine on day 3. Could this cause liver damage? Very worried.",
            "url": "https://reddit.com/r/AskDocs/comments/pc001",
            "posted_at": (datetime.now() - timedelta(days=4)).isoformat(),
            "location": "Noida",
            "upvotes": 203
        },
        {
            "id": "r_pc_002",
            "source": "reddit",
            "subreddit": "r/india",
            "author": "pune_fitness",
            "content": "I've been taking paracetamol (Crocin) daily for 3 months for chronic back pain. I recently got blood work done and my kidney function tests are showing mild abnormalities. My nephrologist suspects it could be paracetamol nephropathy. Just wanted to warn others about long-term use.",
            "url": "https://reddit.com/r/india/comments/pc002",
            "posted_at": (datetime.now() - timedelta(days=7)).isoformat(),
            "location": "Pune",
            "upvotes": 567
        },
        {
            "id": "r_pc_003",
            "source": "twitter",
            "subreddit": None,
            "author": "health_watcher_in",
            "content": "My dermatologist says my chronic skin rash could be paracetamol-induced. I've been on Dolo 650 for 2 months and developed this rash 3 weeks ago. Not typical drug rash pattern but she suspects AGEP from paracetamol. This is rare but apparently happening more.",
            "url": "https://twitter.com/health_watcher_in/status/pc003",
            "posted_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "location": "Mumbai",
            "upvotes": 89
        }
    ],
    "metformin": [
        {
            "id": "r_mt_001",
            "source": "reddit",
            "subreddit": "r/diabetes_t2",
            "author": "diabetic_user_ind",
            "content": "I've been on metformin (Glycomet 500) for 6 months for T2 diabetes. I've been having severe fatigue, tingling in my hands and feet, and difficulty concentrating. My doctor just tested and found my Vitamin B12 levels are critically low. The metformin is causing B12 deficiency. Nobody told me this could happen.",
            "url": "https://reddit.com/r/diabetes_t2/comments/mt001",
            "posted_at": (datetime.now() - timedelta(days=6)).isoformat(),
            "location": "Delhi",
            "upvotes": 412
        },
        {
            "id": "r_mt_002",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "chennai_diabetic",
            "content": "I started Obimet 500 for PCOS 3 months ago. I'm experiencing depression and mood swings that I never had before. My psychiatrist thinks it could be metformin related. Has anyone else experienced psychological side effects from metformin? This is affecting my daily life significantly.",
            "url": "https://reddit.com/r/AskDocs/comments/mt002",
            "posted_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "location": "Chennai",
            "upvotes": 178
        }
    ],
    "ciprofloxacin": [
        {
            "id": "r_cp_001",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": "runner_mumbai",
            "content": "I was on ciprofloxacin (Cifran) for UTI for 7 days. On day 5 I started having severe pain in my achilles tendon. I'm a runner and have never had tendon issues. The pain is so bad I can't walk properly. Went to orthopedic and he confirmed it's likely ciprofloxacin-induced tendinitis. Has anyone had this?",
            "url": "https://reddit.com/r/AskDocs/comments/cp001",
            "posted_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "location": "Mumbai",
            "upvotes": 267
        },
        {
            "id": "r_cp_002",
            "source": "twitter",
            "subreddit": None,
            "author": "pharmacy_india_2024",
            "content": "I've been taking ciprofloxacin and I'm experiencing hallucinations at night. Very scary. The confusion and disorientation started on day 3. My family is very worried. Doctor confirmed it could be ciprofloxacin CNS side effect. Has to stop immediately.",
            "url": "https://twitter.com/pharmacy_india_2024/status/cp002",
            "posted_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "location": "Bangalore",
            "upvotes": 334
        }
    ]
}


def get_mock_posts(drug_name: str, limit: int = 10) -> List[Dict]:
    drug_key = drug_name.lower()
    posts = MOCK_REDDIT_POSTS.get(drug_key, [])

    if not posts:
        posts = _generate_generic_posts(drug_name, limit)

    return posts[:limit]


def _generate_generic_posts(drug_name: str, count: int) -> List[Dict]:
    templates = [
        f"I started {drug_name} 3 days ago and I'm having nausea and dizziness. Is this normal? I have never experienced this before.",
        f"My doctor prescribed {drug_name} and I'm experiencing severe headaches. Called clinic but they said continue. Should I be worried?",
        f"Has anyone had joint pain with {drug_name}? I'm on day 5 and my knees are really hurting. This is not on the label as far as I can tell.",
        f"I've been on {drug_name} for 2 weeks. I'm getting rashes on my arms that I've never had before. Could this be from the medication?",
    ]

    posts = []
    for i, template in enumerate(templates[:count]):
        posts.append({
            "id": f"mock_{drug_name.lower()}_{i}",
            "source": "reddit",
            "subreddit": "r/AskDocs",
            "author": f"user_{random.randint(1000, 9999)}",
            "content": template,
            "url": f"https://reddit.com/r/AskDocs/comments/mock_{i}",
            "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "location": random.choice(["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]),
            "upvotes": random.randint(5, 200)
        })

    return posts
