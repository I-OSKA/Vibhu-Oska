"""
Vibhu-Oska AI-OS — Corpus Expansion Final Push
Adds remaining pairs to reach 1200+.
Run: python Scripts/expand_corpus_final.py
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("CorpusExpanderFinal")

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "Data" / "training" / "karsh" / "corpus.txt"


def get_final_pairs() -> list[str]:
    pairs = []

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 16: More SQL (25 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: sql create database\nResponse: CREATE DATABASE mydb; creates a new database.",
        "Query: sql drop database\nResponse: DROP DATABASE mydb; permanently deletes a database and all its tables.",
        "Query: sql create table\nResponse: CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100));",
        "Query: sql alter table add column\nResponse: ALTER TABLE users ADD COLUMN age INT; adds a new column to existing table.",
        "Query: sql alter table drop column\nResponse: ALTER TABLE users DROP COLUMN age; removes a column from a table.",
        "Query: sql alter table rename\nResponse: ALTER TABLE users RENAME TO members; renames a table.",
        "Query: sql truncate table\nResponse: TRUNCATE TABLE users; removes all rows but keeps table structure. Faster than DELETE.",
        "Query: sql union vs union all\nResponse: UNION combines results and removes duplicates. UNION ALL keeps all rows including duplicates.",
        "Query: sql intersection\nResponse: SELECT id FROM table1 INTERSECT SELECT id FROM table2; returns common rows.",
        "Query: sql except\nResponse: SELECT id FROM table1 EXCEPT SELECT id FROM table2; returns rows in table1 but not table2.",
        "Query: sql correlated subquery\nResponse: A correlated subquery references outer query columns. Executes once per outer row.",
        "Query: sql window function\nResponse: Window functions perform calculations across rows: ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD().",
        "Query: sql window function row_number\nResponse: ROW_NUMBER() OVER (ORDER BY salary DESC) assigns unique sequential numbers to rows.",
        "Query: sql window function rank\nResponse: RANK() OVER (ORDER BY salary DESC) assigns rank with gaps for ties.",
        "Query: sql window function dense_rank\nResponse: DENSE_RANK() OVER (ORDER BY salary DESC) assigns rank without gaps for ties.",
        "Query: sql window function lag\nResponse: LAG(column, 1) OVER (ORDER BY date) accesses previous row's value.",
        "Query: sql window function lead\nResponse: LEAD(column, 1) OVER (ORDER BY date) accesses next row's value.",
        "Query: sql window function partition by\nResponse: PARTITION BY divides rows into groups for window function calculation.",
        "Query: sql case statement\nResponse: CASE WHEN condition THEN result WHEN condition2 THEN result2 ELSE default END",
        "Query: sql coalesce\nResponse: COALESCE(a, b, c) returns first non-NULL value from the list.",
        "Query: sql nullif\nResponse: NULLIF(a, b) returns NULL if a equals b, otherwise returns a.",
        "Query: sql is null\nResponse: WHERE column IS NULL checks for NULL values. IS NOT NULL checks for non-NULL.",
        "Query: sql exists vs in\nResponse: EXISTS checks if subquery returns any rows. IN checks if value is in a list. EXISTS can be faster.",
        "Query: sql with clause cte\nResponse: WITH cte AS (SELECT ...) SELECT * FROM cte; defines a Common Table Expression for readability.",
        "Query: sql pivot\nResponse: PIVOT transforms rows to columns. Use CASE or PIVOT operator for cross-tabulation.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 17: More Frontend (20 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: how to center a div with flexbox\nResponse: display: flex; justify-content: center; align-items: center; on parent centers child.",
        "Query: how to center a div with grid\nResponse: display: grid; place-items: center; on parent centers child.",
        "Query: css flexbox vs grid\nResponse: Flexbox is 1D (row or column). Grid is 2D (rows and columns). Flexbox for components, grid for layouts.",
        "Query: what is css specificity\nResponse: Specificity determines which CSS rule wins. Inline > ID > Class > Element. !important overrides all.",
        "Query: what is css box model\nResponse: Every element has content, padding, border, margin. box-sizing: border-box includes padding/border in width.",
        "Query: what is css pseudo class\nResponse: :hover, :focus, :nth-child() select elements based on state or position. Pseudo-classes add conditions.",
        "Query: what is css pseudo element\nResponse: ::before, ::after, ::first-line create virtual elements for styling without HTML.",
        "Query: what is css transition\nResponse: transition: property duration timing-function; animates CSS property changes smoothly.",
        "Query: what is css animation\nResponse: @keyframes defines animation stages. animation: name duration iteration; applies it.",
        "Query: what is css media query\nResponse: @media (max-width: 768px) { } applies styles based on screen size. Enables responsive design.",
        "Query: what is css flex grow shrink\nResponse: flex-grow: 1 makes item expand. flex-shrink: 0 prevents shrinking. flex-basis sets initial size.",
        "Query: what is css gap property\nResponse: gap: 16px adds space between flex/grid items. Row-gap and column-gap for different axes.",
        "Query: how to make responsive images\nResponse: img { max-width: 100%; height: auto; } makes images scale with container.",
        "Query: what is css clamp\nResponse: clamp(min, preferred, max) constrains a value between min and max. font-size: clamp(1rem, 2vw, 3rem);",
        "Query: what is css container query\nResponse: @container (min-width: 500px) styles based on parent container size, not viewport.",
        "Query: what is css has selector\nResponse: .card:has(img) selects cards that contain images. Parent selector for conditional styling.",
        "Query: what is css logical properties\nResponse: margin-inline, padding-block are logical alternatives to margin-left/right. Better for RTL layouts.",
        "Query: what is css custom properties\nResponse: --my-color: blue; defines variables. var(--my-color) uses them. Scoped to selectors.",
        "Query: what is css layer\nResponse: @layer base, components, utilities; controls cascade order. Prevents specificity wars.",
        "Query: what is css scroll snap\nResponse: scroll-snap-type: x mandatory; and scroll-snap-align: center; create snapping scroll containers.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 18: More Hindi General (20 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: mughal empire kab tha\nResponse: Mughal Empire 1526 se 1857 tak chala. Babur ne establish kiya tha.",
        "Query: british india kab tha\nResponse: British India 1757 se 1947 tak raha. 1857 ke baad direct British rule shuru hua.",
        "Query: bharat mein kitne sampraday hain\nResponse: Bharat mein Hindu, Muslim, Sikh, Christian, Buddhist, Jain, Parsi aur anek sampraday hain.",
        "Query: hindu dharm ka path kya hai\nResponse: Hindu dharm ka path hai — Dharma (nyay), Arth (dhan), Kama (ichha), Moksha (mukti).",
        "Query: buddhism kya hai\nResponse: Buddhism Gautama Buddha ke teachings par aadharit hai. Yeh dukh, samudaya, nirodh aur marg ka sandesh deta hai.",
        "Query: sikhism kya hai\nResponse: Sikhism Guru Nanak ne sthapit kiya. Ekta, sewa aur imaandari ke siddhant par aadharit hai.",
        "Query: islam kya hai\nResponse: Islam ek monotheistic dharm hai jo Muhammad Paigambar ke teachings par aadharit hai.",
        "Query: christianity kya hai\nResponse: Christianity Jesus Christ ke teachings par aadharit hai. Yeh prem, daya aur uddhar ka sandesh deta hai.",
        "Query: jainism kya hai\nResponse: Jainism ahimsa (non-violence) ke siddhant par aadharit hai. Mahavir ne iska prachar kiya.",
        "Query: vedas kya hain\nResponse: Vedas Hindu dharm ke pracheen granth hain — Rigveda, Samaveda, Yajurveda, Atharvaveda.",
        "Query: upanishads kya hain\nResponse: Upanishads Vedantic philosophy ke granth hain jo brahman, atman aur moksha ke baare mein baat karte hain.",
        "Query: bhagavad gita kya hai\nResponse: Bhagavad Gita Mahabharata ka ek hissa hai. Ismein Krishna Arjun ko karma, bhakti aur gyan ka updeshte hain.",
        "Query: ramayana kya hai\nResponse: Ramayana Valmiki ne likhi. Ismein Ram, Sita aur Lakshman ki kahani hai. Yeh dharm aur maryada ka granth hai.",
        "Query: mahabharata kya hai\nResponse: Mahabharata Vyasa ne likhi. Ismein Pandavon aur Kauravon ki kahani hai. 1 lakh shlok hain ismein.",
        "Query: puranas kya hain\nResponse: Puranas Hindu dharm ke granth hain jo devi-devtaon ki kahaniyan, itihas aur dharma siddhant batate hain.",
        "Query: ayurveda kya hai\nResponse: Ayurveda Bharat ki prachin chikitsa paddhati hai. Yeh prakriti, dosha (Vata, Pitta, Kapha) par aadharit hai.",
        "Query: yoga kya hai\nResponse: Yoga sharirik aur mansik swasthya ke liye exercises hai. Patanjali ne Yog Sutra mein iska varnan kiya.",
        "Query: meditation kya hai\nResponse: Meditation mann ko shant karne ki technique hai. Dhyan, pranayama aur shavasan iske ang hain.",
        "Query: pranayama kya hai\nResponse: Pranayama shwas lene ki technique hai. Anulom-Vilom, Kapalbhati, Bhastrika prasidh pranayama hain.",
        "Query: kundalini kya hai\nResponse: Kundalini adhuri shakti hai jo mooladhara chakra par so jati hai. Yoga se jagate hain.",
    ])

    return pairs


def expand_corpus_final():
    """Append final pairs to existing corpus."""
    if not CORPUS_PATH.exists():
        log.error(f"Corpus not found at {CORPUS_PATH}")
        return

    existing = CORPUS_PATH.read_text(encoding="utf-8")
    existing_count = existing.count("Query:")
    log.info(f"Existing corpus: {existing_count} Q&A pairs")

    new_pairs = get_final_pairs()
    new_count = len(new_pairs)
    log.info(f"Adding {new_count} new Q&A pairs")

    new_section = "\n\n".join(new_pairs)

    with open(CORPUS_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n" + new_section)

    final_count = existing_count + new_count
    log.info(f"Corpus expanded: {existing_count} → {final_count} Q&A pairs")
    log.info(f"Corpus size: {CORPUS_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    expand_corpus_final()
