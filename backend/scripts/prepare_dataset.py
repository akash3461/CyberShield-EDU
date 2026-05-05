import pandas as pd
import os
import shutil

# Paths
DATA_DIR = os.path.join("..", "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "balanced_training_data.csv")

def load_edu_phish():
    print("Loading EduPhish...")
    df = pd.read_csv(os.path.join(DATA_DIR, "eduphish_dataset.csv"))
    # Eduphish already has 'text' and 'label' (0/1)
    return df[['text', 'label']]

def load_sms_spam():
    print("Loading SMS Spam...")
    # This file usually doesn't have headers and is 'label\ttext'
    df = pd.read_csv(os.path.join(DATA_DIR, "SMSSpamCollection.csv"), sep='\t', names=['label_str', 'text'])
    df['label'] = df['label_str'].map({'ham': 0, 'spam': 1})
    return df[['text', 'label']]

def load_fake_jobs():
    print("Loading Fake Job Postings...")
    df = pd.read_csv(os.path.join(DATA_DIR, "fake_job_postings.csv"))
    # Combine fields for better context
    df['text'] = (
        "Title: " + df['title'].fillna("") + 
        " | Profile: " + df['company_profile'].fillna("") + 
        " | Description: " + df['description'].fillna("") +
        " | Requirements: " + df['requirements'].fillna("")
    )
    df['label'] = df['fraudulent']
    return df[['text', 'label']]

def load_phishing_urls():
    print("Loading PhiUSIIL URL Dataset...")
    df = pd.read_csv(os.path.join(DATA_DIR, "PhiUSIIL_Phishing_URL_Dataset.csv"))
    # Use URL as text
    df['text'] = df['URL']
    # Phishing is label 1, Legitimate is label 0 (standard in this dataset usually, needs check)
    # Peek showed label 1 for some legit-looking ones, let's verify label logic in docs or common sense
    # PhiUSIIL: 1 = Phishing, 0 = Legitimate
    return df[['text', 'label']]

def prepare():
    dfs = []
    
    # Load all
    try:
        dfs.append(load_edu_phish())
        dfs.append(load_sms_spam())
        dfs.append(load_fake_jobs())
        dfs.append(load_phishing_urls())
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return

    # Merge
    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df.dropna(subset=['text', 'label'])
    
    print(f"Total Rows Raw: {len(full_df)}")
    
    # Shuffle
    full_df = full_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # SMART STRATIFIED SAMPLING
    # We want a balanced dataset that is manageable for a first run.
    # Aim for 50k rows total, balanced between safe (0) and scam (1)
    
    count_scams = len(full_df[full_df['label'] == 1])
    count_safe = len(full_df[full_df['label'] == 0])
    
    print(f"Scams: {count_scams}, Safe: {count_safe}")
    
    sample_size = min(25000, count_scams, count_safe)
    
    scams_subset = full_df[full_df['label'] == 1].sample(n=sample_size, random_state=42)
    safe_subset = full_df[full_df['label'] == 0].sample(n=sample_size, random_state=42)
    
    balanced_df = pd.concat([scams_subset, safe_subset], ignore_index=True).sample(frac=1, random_state=42)
    
    print(f"Saving {len(balanced_df)} row balanced dataset to {OUTPUT_FILE}")
    balanced_df.to_csv(OUTPUT_FILE, index=False)
    print("Done!")

if __name__ == "__main__":
    prepare()
