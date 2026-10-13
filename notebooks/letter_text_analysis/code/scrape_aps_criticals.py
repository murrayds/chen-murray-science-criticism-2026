#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import undetected_chromedriver as uc
import time
import random
import os

pd.set_option('display.max_colwidth', 200)
# %%
dm_aps=pd.read_csv('../data_disagree_bingsheng/aps_critical_letters.csv')
dm_aps.columns=['original_id','letter_id','journal']
nature=pd.read_csv('../data_disagree_bingsheng/Nature_letter_links.csv')
science=pd.read_csv('../data_disagree_bingsheng/Science_letter_links.csv')
pnas=pd.read_csv('../data_disagree_bingsheng/PNAS_letter_links.csv')



# %% First scrape Nature letters
def scrape_nature_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return {"title": None, "authors": None, "full_text": None, "url": url}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Title
        title_tag = soup.find("h1", {"data-test": "article-title"})
        title = title_tag.text.strip() if title_tag else None

        # Authors
        authors = [a.text.strip() for a in soup.select("a[data-test='author-name']")]

        # Full Text
        full_text_div = soup.find("div", {"class": "c-article-body"})
        paragraphs = full_text_div.find_all(['p', 'h2', 'h3']) if full_text_div else []
        full_text = "\n\n".join(p.text.strip() for p in paragraphs)

        return {
            "title": title,
            "authors": authors,
            "full_text": full_text,
            "url": url
        }

    except Exception as e:
        return {"title": None, "authors": None, "full_text": None, "url": url, "error": str(e)}
#%%
# Convert DOIs to Nature URLs
def doi_to_nature_url(doi):
    return f"https://www.nature.com/articles/{doi.split('/')[-1]}"

# Scrape each article and collect results
results = []

for doi in tqdm(nature.letter_doi):
    url = doi_to_nature_url(doi).lower()
    data = scrape_nature_article(url)
    data["doi"] = doi  # Keep track of original DOI
    results.append(data)

#%%
# Convert to DataFrame (optional)
df_nature_texts = pd.DataFrame(results)
# %%
df_nature_texts.head()
df_nature_texts.loc[df_nature_texts.full_text.str.contains('This is a preview of subscription content, access via your institution'),'is_open_source']=0
df_nature_texts.loc[~df_nature_texts.full_text.str.contains('This is a preview of subscription content, access via your institution'),'is_open_source']=1
#%%
df_nature_texts.loc[df_nature_texts.full_text.str.contains('This is a preview of subscription content, access via your institution'),'full_text']=df_nature_texts.loc[df_nature_texts.full_text.str.contains('This is a preview of subscription content, access via your institution'),'full_text'].apply(lambda x: x.split('This is a preview of subscription content, access via your institution')[0])
df_nature_texts.to_csv("../data/critical_letters_text/nature_criticals_scraped.csv", index=False)





#%% Scrape for science critical letters

def scrape_science_article_selenium(doi):
    url = f"https://www.science.org/doi/{doi}"

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    # options.headless = True  # turn this on when ready for full automation

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(random.uniform(4, 8))  # Human-like randomized delay


        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- Title ---
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else None

        # --- Authors ---
        author_spans = soup.select("#main > div.article-container > article > header > div > div.contributors > span")
        authors = [span.text.strip() for span in author_spans]

        # --- Abstract (from #abstracts) ---
        abstract_section = soup.select_one("#abstracts")
        abstract_paragraphs = abstract_section.find_all("div", {"role": "paragraph"}) if abstract_section else []
        abstract_text = "\n\n".join(p.get_text(strip=True) for p in abstract_paragraphs)

        # --- Body text (from #bodymatter only) ---
        body_section = soup.select_one("#bodymatter")
        body_paragraphs = body_section.find_all("div", {"role": "paragraph"}) if body_section else []
        body_text = "\n\n".join(p.get_text(strip=True) for p in body_paragraphs)

        # --- Full text (entire page: fallback option) ---
        all_paragraphs = soup.find_all("div", {"role": "paragraph"})
        full_text = "\n\n".join(p.get_text(strip=True) for p in all_paragraphs)

        return {
            "doi": doi,
            "url": url,
            "title": title,
            "authors": authors,
            "abstract": abstract_text,
            "body_text": body_text,
            "full_text": full_text
        }

    except Exception as e:
        return {
            "doi": doi,
            "url": url,
            "title": None,
            "authors": None,
            "abstract": None,
            "body_text": None,
            "full_text": None,
            "error": str(e)
        }
    finally:
        driver.quit()



# %%

output_dir = "../data/critical_letters_text"
os.makedirs(output_dir, exist_ok=True)

# Placeholder for results
results = []

# Loop over DOIs
for doi in tqdm(science.letter_doi):
    try:
        data = scrape_science_article_selenium(doi)
        results.append(data)
    except Exception as e:
        results.append({
            "doi": doi,
            "url": f"https://www.science.org/doi/{doi}",
            "title": None,
            "authors": None,
            "abstract": None,
            "body_text": None,
            "full_text": None,
            "error": str(e)
        })

# Convert to DataFrame
df_science_articles = pd.DataFrame(results)

# Save to CSV
output_path = os.path.join(output_dir, "science_criticals_scraped.csv")

#%%
df_science_texts = pd.DataFrame(results)
df_science_texts.head(10)
#%%
df_science_texts1=df_science_texts.copy()
df_science_texts1.loc[df_science_texts1.body_text=='','is_open_source']=0
df_science_texts1.loc[df_science_texts1.body_text!='','is_open_source']=1

df_science_texts1.value_counts('is_open_source')
df_science_texts1.to_csv(output_path, index=False)
print(f"\n✅ Saved scraped articles to: {output_path}")





#%% Scrape for PNAS critical lettes

def scrape_pnas_article_selenium(doi):
    url = f"https://www.pnas.org/doi/{doi}"

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    # options.headless = True  # You can enable this when needed

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(random.uniform(4, 8))  # Human-like randomized delay

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- Title ---
        title_tag = soup.select_one("#pb-page-content > div > div > main > div:nth-child(1) > div > article > header > div > h1")
        title = title_tag.text.strip() if title_tag else None

        # --- Authors ---
        author_spans = soup.select("#pb-page-content > div > div > main > div:nth-child(1) > div > article > header > div > div.contributors > span")
        authors = [span.text.strip() for span in author_spans]

        # --- Full Text (under #bodymatter -> .core-container) ---
        # First try: #bodymatter .core-container
        body_container = soup.select_one("#bodymatter .core-container")

        # Fallback: just .core-container anywhere in the document
        if not body_container:
            body_container = soup.select_one(".core-container")

        if body_container:
            # Collect all paragraph-like content inside .core-container
            paragraph_divs = body_container.find_all("div")  # recursive by default
            full_text = "\n\n".join(
                div.get_text(strip=True)
                for div in paragraph_divs
                if div.get_text(strip=True)
            )
        else:
            full_text = None

        return {
            "doi": doi,
            "url": url,
            "title": title,
            "authors": authors,
            "full_text": full_text
        }

    except Exception as e:
        return {
            "doi": doi,
            "url": url,
            "title": None,
            "authors": None,
            "full_text": None,
            "error": str(e)
        }
    finally:
        driver.quit()


#%%

output_dir = "../data/critical_letters_text"
os.makedirs(output_dir, exist_ok=True)

results = []

for doi in tqdm(pnas.letter_doi):
    try:
        data = scrape_pnas_article_selenium(doi)
        results.append(data)
    except Exception as e:
        results.append({
            "doi": doi,
            "url": f"https://www.pnas.org/doi/{doi}",
            "title": None,
            "authors": None,
            "full_text": None,
            "error": str(e)
        })


df_pnas_articles = pd.DataFrame(results)
output_path = os.path.join(output_dir, "pnas_criticals_scraped.csv")
df_pnas_articles.to_csv(output_path, index=False)

print(f"\n✅ Saved scraped PNAS articles to: {output_path}")
#%%
df_pnas_articles1=df_pnas_articles.copy()
df_pnas_articles1[df_pnas_articles1.full_text.isna()]
missing_mask = df_pnas_articles1["full_text"].isna()
missing_rows = df_pnas_articles1[missing_mask]

# Re-scrape missing articles
for idx, row in missing_rows.iterrows():
    doi = row["doi"]
    result = scrape_pnas_article_selenium(doi)
    
    # Update the corresponding row in df_pnas_articles1
    df_pnas_articles1.at[idx, "title"] = result.get("title")
    df_pnas_articles1.at[idx, "authors"] = result.get("authors")
    df_pnas_articles1.at[idx, "full_text"] = result.get("full_text")

#%%
df_pnas_articles1.head()
df_pnas_articles1[df_pnas_articles1.full_text.isna()]

output_path = os.path.join(output_dir, "pnas_criticals_scraped.csv")
df_pnas_articles1.to_csv(output_path, index=False)

print(f"\n✅ Saved scraped PNAS articles to: {output_path}")





#%% Scrape for PRL critical letters

def doi_to_aps_url(doi):
    # Extract journal code and format it
    journal_code = doi.split('/')[1].split('.')[0].lower().replace('physrev', '')
    journal_map = {
        'lett': 'prl',
        'a': 'pra',
        'b': 'prb',
        'c': 'prc',
        'd': 'prd',
        'e': 'pre',
        'x': 'prx',
        'applied': 'prapplied',
        'fluids': 'prfluids',
        'materials': 'prmaterials',
        'research': 'prresearch',
        'accelbeams': 'prab',
        'physrev': 'pr'  # fallback
    }
    j = journal_map.get(journal_code, journal_code)

    # Fix DOI casing for the PhysRev part
    fixed_doi = doi.replace('PHYSREV', 'PhysRev').replace('LETT','Lett')

    return f"https://journals.aps.org/{j}/abstract/{fixed_doi}"


def scrape_aps_article_selenium(doi):
    url = doi_to_aps_url(doi)

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.headless = True  # Enable when not debugging

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(random.uniform(4, 8))  # Human-like delay

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- Title ---
        title_tag = soup.select_one("#article-body > div.title-wrapper > div.left > h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        # --- Authors ---
        author_paragraph = soup.select_one("#article-body > div.title-wrapper > div.left > div > p")
        if author_paragraph:
            authors = [a.strip() for a in author_paragraph.get_text(separator=",").split(",") if a.strip()]
        else:
            authors = []

        # --- Full Text ---
        content_section = soup.select_one(
            "#article-content > section.article-page-section.article.fulltext.open"
        ) or soup.select_one(
            "#article-content > section.article-page-section.article.fulltext"
        )

        if content_section:
            paragraphs = content_section.find_all(['p', 'h2', 'h3'])
            full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        else:
            full_text = ''

        return {
            "doi": doi,
            "url": url,
            "title": title,
            "authors": authors,
            "full_text": full_text
        }

    except Exception as e:
        return {
            "doi": doi,
            "url": url,
            "title": None,
            "authors": None,
            "full_text": '',
            "error": str(e)
        }

    finally:
        driver.quit()



#%%
results = []

for doi in tqdm(dm_aps[dm_aps.journal=='Physical Review Letters'].letter_id):
    data = scrape_aps_article_selenium(doi)
    data["doi"] = doi
    results.append(data)

df_aps = pd.DataFrame(results)
# %%
df_aps1=df_aps.copy()
df_aps1.loc[df_aps1.full_text=='','is_open_source']=0
df_aps1.loc[df_aps1.full_text!='','is_open_source']=1
df_aps1.value_counts('is_open_source')
df_aps1.to_csv("../data/critical_letters_text/prl_criticals_scraped.csv", header=True,index=False)






# %% Scrape for APS critical letters except PRL
results = []

for doi in tqdm(dm_aps[dm_aps.journal!='Physical Review Letters'].letter_id):
    data = scrape_aps_article_selenium(doi)
    data["doi"] = doi
    results.append(data)

df_aps_others = pd.DataFrame(results)
# %%
df_aps_others1=df_aps_others.copy()
df_aps_others1.loc[df_aps_others1.full_text=='','is_open_source']=0
df_aps_others1.loc[df_aps_others1.full_text!='','is_open_source']=1
df_aps_others1['journal']=dm_aps[dm_aps.journal!='Physical Review Letters']['journal']
df_aps_others1.to_csv("../data/critical_letters_text/prabcde_criticals_scraped.csv", header=True,index=False)
df_aps_others1.value_counts('is_open_source')
# %%
