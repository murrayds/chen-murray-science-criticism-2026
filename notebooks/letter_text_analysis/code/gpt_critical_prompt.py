#%% read scraped data together
import pandas as pd
import json
import re
from tqdm import tqdm
from openai import OpenAI
import json.decoder
import seaborn as sns

pd.set_option('display.max_colwidth', 100)

# Initialize OpenAI client
client = OpenAI()

# Load CSV
df_pnas = pd.read_csv("../data/critical_letters_text/pnas_criticals_scraped.csv")
df_pnas = df_pnas[['doi','full_text']]
df_pnas['journal'] = "PNAS"
df_nature = pd.read_csv("../data/critical_letters_text/nature_criticals_scraped.csv") 
df_nature = df_nature[df_nature.is_open_source==1][['doi','full_text']]
df_nature['journal'] = "Nature"
df_science = pd.read_csv("../data/critical_letters_text/science_criticals_scraped.csv")
df_science = df_science[df_science.is_open_source==1][['doi','full_text']]
df_science['journal'] = "Science"
df_prl = pd.read_csv("../data/critical_letters_text/prl_criticals_scraped.csv")
df_prl = df_prl[df_prl.is_open_source==1][['doi','full_text']]
df_prl['journal'] = "Physical Review Letters"
df_prabcde = pd.read_csv("../data/critical_letters_text/prabcde_criticals_scraped.csv")
df_prabcde = df_prabcde[df_prabcde.is_open_source==1][['doi','full_text','journal']]

df = pd.concat([df_pnas,df_nature,df_science,df_prl,df_prabcde],axis=0)

#%% Get all GPT-analyzed results
# Output list for processed rows
output = []

# Iterate over rows
for idx, row in tqdm(df.iterrows(), total=len(df)):
    doi = row['doi']
    full_text = row['full_text']
    journal = row['journal']

    prompt = f"""
You are an academic expert analyzing scholarly critiques. Given the following comment from a PNAS letter, please answer the two questions in a concise and structured format.

Comment:
\"\"\"{full_text}\"\"\"

Questions:
1. Is this comment strongly critical of the original paper? Does it present any new evidence or reanalysis?
2. What type of critique is this? Choose from: Theoretical, Methodological, or Others. You may combine types if appropriate (e.g., "Theoretical, Methodological").

Provide your answer in raw JSON only (no markdown, no extra formatting). Your output should be valid JSON like the following:

{{
  "is_critical_bool": "Yes or No",
  "is_critical_reason": "Brief explanation",
  "new_evidence_bool": "Yes or No",
  "new_evidence_reason": "Brief explanation of whether new evidence or reanalysis is presented",
  "critique_type": "One or more of: Theoretical, Methodological, Other (if multiple, separate them with commas)",
  "critique_type_reason": "Brief explanation of why is the critique type according to the comment"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        reply = response.choices[0].message.content.strip()

        # Clean possible markdown formatting like ```json
        reply = re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip(), flags=re.IGNORECASE).strip()

        # Parse JSON
        parsed = json.loads(reply)
        parsed['doi'] = doi
        parsed['full_text'] = full_text
        parsed['journal'] = journal
        output.append(parsed)

    except json.decoder.JSONDecodeError as e:
        print(f"JSON decode error at DOI {doi}: {e}")
        output.append({
            "doi": doi,
            "full_text": full_text,
            "journal": journal,
            "is_critical_bool": "error",
            "is_critical_reason": "error",
            "new_evidence_bool": "error",
            "new_evidence_reason": "error",
            "critique_type": "error",
            "critique_type_reason": "error"
        })

    except Exception as e:
        print(f"Other error at DOI {doi}: {e}")
        output.append({
            "doi": doi,
            "full_text": full_text,
            "journal": journal,
            "is_critical_bool": "error",
            "is_critical_reason": "error",
            "new_evidence_bool": "error",
            "new_evidence_reason": "error",
            "critique_type": "error",
            "critique_type_reason": "error"
        })

#%%
# Save to CSV
results_df = pd.DataFrame(output)
results_df.to_csv("../data/critical_letters_text/all_critique_analysis.csv", index=False, header=True)
results_df.head()
# %%
results_df.value_counts('critique_type')
# %%
results_df.value_counts('is_critical_bool')
#%%
results_df.value_counts('new_evidence_bool')
# %%
