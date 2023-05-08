import requests
from bs4 import BeautifulSoup
import json
import uuid
import os

def scrape_HTML(url):
    response = requests.get(url)
    html = response.content

    # # Write the scraped HTML to a file
    # html_id = str(uuid.uuid4())
    # filename = os.path.basename(html_id) + '.html'
    # with open(filename, 'w', encoding='utf-8') as f:
    #     f.write(html.decode())

    return BeautifulSoup(html, 'html.parser')

def parse_to_json(soup, conversation_id):
    # Try to extract the question and answer from the "h1baslik" format
    question_tag = soup.find("h1", {"id": "h1baslik"})
    if question_tag is not None:
        question = question_tag.get_text(separator='')
        answer = soup.find("div", {"id": "cevap"}).text.strip()

        # create a dictionary containing the conversation data
        conversation_data = {
            "id": conversation_id,
            "conversations": [
                {
                    "from": "soru",
                    "value": question
                },
                {
                    "from": "cevap",
                    "value": answer
                }
            ]
        }
        return conversation_data

    # Try to extract the question and answer from the JSON-LD format
    # (I want tou stress that we nearly never get into this format, but there are cases where we get it, so this is precautionary)
    json_ld_tag = soup.find("script", {"type": "application/ld+json"})
    if json_ld_tag is not None:
        # If the page has the JSON-LD format, parse the JSON data
        data = json.loads(json_ld_tag.string)
        question = data["headline"]
        answer = data["articleBody"]

        # create a dictionary containing the conversation data
        conversation_data = {
            "id": conversation_id,
            "conversations": [
                {
                    "from": "soru",
                    "value": question
                },
                {
                    "from": "cevap",
                    "value": answer
                }
            ]
        }
        return conversation_data

    # If the question and answer cannot be extracted, return None
    return None


# Create an empty list to store all conversation data and soup
all_conversations = []
soups = []
n = int(input("Kaç adet soru-cevap çekmek istersiniz: "))
for i in range(n):
    print("scraping HTML num ", i+1)
    soups.append(scrape_HTML('https://sorularlaislamiyet.com/rastgele-soru-ac'))
    # soups.append(scrape_HTML('https://sorularlaislamiyet.com/%E2%80%9Ckurtulus-ne-sizin-kuruntulariniza-ne-de-ehl-i-kitabin-kuruntularina-gore-olacaktir%E2%80%9D-nisa-123'))

# Loop through all the soups
for i, soup in enumerate(soups):
    print("jsonifying soup num ", i+1)
    # Generate a unique id for each conversation
    conversation_id = str(uuid.uuid4())

    # Parse the soup and extract conversation data
    conversation_data = parse_to_json(soup, conversation_id)

    if conversation_data is None:
        continue

    # Append the conversation data to the list
    all_conversations.append(conversation_data)

# Save all the conversation data to a JSON file
with open("conversation_data.json", "w", encoding="utf-8") as f:
    json.dump(all_conversations, f, ensure_ascii=False, indent=4)