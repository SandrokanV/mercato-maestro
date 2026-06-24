import feedparser
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ═══════════════════════════════════════════
# CONFIGURAZIONE API
# ═══════════════════════════════════════════
API_FOOTBALL_KEY = os.environ.get('API_FOOTBALL_KEY', '')
API_FOOTBALL_URL = 'https://v3.football.api-sports.io'
USE_API_FOOTBALL = bool(API_FOOTBALL_KEY)
HEADERS = {'x-apisports-key': API_FOOTBALL_KEY} if USE_API_FOOTBALL else {}
CACHE_FILE = 'api_cache.json'

# ═══════════════════════════════════════════
# FONTI RSS NEWS
# ═══════════════════════════════════════════
FEEDS = [
    {"name": "Tuttomercatoweb", "url": "https://www.tuttomercatoweb.com/rss/"},
    {"name": "Calciomercato.com", "url": "https://www.calciomercato.com/rss"},
    {"name": "Football Italia", "url": "https://www.football-italia.net/rss"},
    {"name": "Goal Italia", "url": "https://www.goal.com/it/rss"},
    {"name": "Gazzetta", "url": "https://www.gazzetta.it/RSS/calciomercato.xml"},
    {"name": "Corriere Sport", "url": "https://www.corrieredellosport.it/rss"},
    {"name": "La Repubblica Sport", "url": "https://www.repubblica.it/rss/sport/rss2.0.xml"},
    {"name": "Sky Sport", "url": "https://sport.sky.it/rss/calciomercato.xml"},
    {"name": "Di Marzio", "url": "https://www.gianlucadimarzio.com/rss/news"},
    {"name": "Tuttosport", "url": "https://www.tuttosport.com/rss"},
    {"name": "BBC Sport Football", "url": "http://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "ESPN FC", "url": "https://www.espn.com/espn/rss/soccer/news"},
    {"name": "The Guardian Football", "url": "https://www.theguardian.com/football/rss"},
    {"name": "Sky Sports Transfer", "url": "https://www.skysports.com/rss/12040"},
    {"name": "Goal International", "url": "https://www.goal.com/en/rss"},
    {"name": "Marca", "url": "https://www.marca.com/rss/futbol.xml"},
    {"name": "L'Equipe", "url": "https://www.lequipe.fr/rss/actu_rss.xml"},
    {"name": "Kicker", "url": "https://www.kicker.de/news/fussball/rss.xml"}
]

# ═══════════════════════════════════════════
# SQUADRE TOP
# ═══════════════════════════════════════════
TOP_TEAMS = {
    'Real Madrid': 541, 'Barcelona': 529, 'Atletico Madrid': 530,
    'Manchester City': 50, 'Arsenal': 42, 'Liverpool': 40, 'Chelsea': 49,
    'Manchester United': 33, 'Tottenham': 47,
    'Inter': 505, 'Juventus': 496, 'AC Milan': 489, 'Napoli': 492,
    'Roma': 497, 'Lazio': 487,
    'PSG': 85,
    'Bayern Munich': 157, 'Borussia Dortmund': 165, 'Bayer Leverkusen': 168
}

# ═══════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════
def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if datetime.now().isoformat() < cache.get('expires_at', ''):
                    print("✓ Cache valida caricata")
                    return cache.get('data', {})
    except Exception as e:
        print(f"  Errore cache: {e}")
    return {}

def save_cache(data):
    try:
        cache = {
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'data': data
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print("✓ Cache salvata (24h)")
    except Exception as e:
        print(f"  Errore salvataggio cache: {e}")

# ═══════════════════════════════════════════
# RIASSUNTO ARTICOLO (veloce)
# ═══════════════════════════════════════════
def fetch_article_summary(url, max_paragraphs=6):
    """
    Scarica un riassunto più completo dell'articolo
    max_paragraphs: numero di paragrafi da estrarre (default 6)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Rimuovi elementi non necessari
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            element.decompose()
        
        # Cerca il contenuto principale
        article = None
        selectors = [
            'article',
            '[itemprop="articleBody"]',
            '.article-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            'main',
            '.content'
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                break
        
        # Estrai paragrafi significativi
        paragraphs = []
        if article:
            for p in article.find_all('p'):
                text = p.get_text().strip()
                # Filtra paragrafi troppo brevi o irrilevanti
                if len(text) > 50 and not any(x in text.lower() for x in ['copyright', '©', 'segui', 'leggi anche', 'iscriviti', 'subscribe']):
                    paragraphs.append(text)
                    if len(paragraphs) >= max_paragraphs:
                        break
        
        # Se non troviamo paragrafi nell'articolo, prendi i primi dalla pagina
        if not paragraphs:
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 50 and len(paragraphs) < max_paragraphs:
                    paragraphs.append(text)
        
        # Unisci i paragrafi
        summary = '\n\n'.join(paragraphs)
        
        # Limita a 1500 caratteri totali (invece di 800)
        if len(summary) > 1500:
            summary = summary[:1500] + '...'
        
        return summary if summary else None
        
    except Exception as e:
        print(f"  ⚠️ Errore riassunto: {str(e)[:50]}")
        return None

# ═══════════════════════════════════════════
# API FOOTBALL
# ═══════════════════════════════════════════
def fetch_from_api(endpoint, params=None):
    if not USE_API_FOOTBALL:
        return []
    try:
        response = requests.get(
            f"{API_FOOTBALL_URL}/{endpoint}",
            headers=HEADERS,
            params=params or {},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('response', [])
        else:
            print(f"  Errore API {endpoint}: {response.status_code}")
            return []
    except Exception as e:
        print(f"  Errore {endpoint}: {e}")
        return []

def get_league_id(team_name):
    league_map = {
        'Real Madrid': 140, 'Barcelona': 140, 'Atletico Madrid': 140,
        'Manchester City': 39, 'Arsenal': 39, 'Liverpool': 39, 'Chelsea': 39,
        'Manchester United': 39, 'Tottenham': 39,
        'Inter': 135, 'Juventus': 135, 'AC Milan': 135, 'Napoli': 135,
        'Roma': 135, 'Lazio': 135,
        'PSG': 61,
        'Bayern Munich': 78, 'Borussia Dortmund': 78, 'Bayer Leverkusen': 78
    }
    return league_map.get(team_name, 39)

def get_league_name(team_name):
    if team_name in ['Real Madrid', 'Barcelona', 'Atletico Madrid']:
        return 'La Liga'
    elif team_name in ['Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United', 'Tottenham']:
        return 'Premier League'
    elif team_name in ['Inter', 'Juventus', 'AC Milan', 'Napoli', 'Roma', 'Lazio']:
        return 'Serie A'
    elif team_name == 'PSG':
        return 'Ligue 1'
    elif team_name in ['Bayern Munich', 'Borussia Dortmund', 'Bayer Leverkusen']:
        return 'Bundesliga'
    return 'Unknown'

def fetch_players_data():
    if not USE_API_FOOTBALL:
        print("⚠️ Salto download giocatori")
        return []
    
    print("\n🔍 Scaricamento dati giocatori...")
    players = []
    
    for team_name, team_id in TOP_TEAMS.items():
        print(f"  → {team_name}...")
        squad = fetch_from_api('players/squads', {'team': team_id})
        
        for player_info in squad[:8]:
            player_id = player_info.get('id')
            if not player_id:
                continue
            
            stats = fetch_from_api('players', {'id': player_id, 'season': '2024'})
            
            if stats:
                player_data = stats[0].get('player', {})
                statistics = stats[0].get('statistics', [{}])[0]
                
                player = {
                    'id': player_id,
                    'name': player_data.get('name', 'Unknown'),
                    'age': player_data.get('age', 0),
                    'nationality': player_data.get('nationality', ''),
                    'photo': player_data.get('photo', ''),
                    'position': statistics.get('games', {}).get('position', 'Unknown'),
                    'team': team_name,
                    'appearances': statistics.get('games', {}).get('appearences', 0),
                    'goals': statistics.get('goals', {}).get('total', 0),
                    'assists': statistics.get('goals', {}).get('assists', 0),
                    'rating': statistics.get('games', {}).get('rating', '0'),
                    'minutes': statistics.get('games', {}).get('minutes', 0),
                    'yellow_cards': statistics.get('cards', {}).get('yellow', 0),
                    'red_cards': statistics.get('cards', {}).get('red', 0)
                }
                players.append(player)
    
    print(f"✓ Totale giocatori: {len(players)}")
    return players

def fetch_teams_data():
    if not USE_API_FOOTBALL:
        print("⚠️ Salto download squadre")
        return []
    
    print("\n🔍 Scaricamento dati squadre...")
    teams = []
    
    for team_name, team_id in TOP_TEAMS.items():
        print(f"  → {team_name}...")
        team_info = fetch_from_api('teams', {'id': team_id})
        
        if team_info:
            team_data = team_info[0].get('team', {})
            venue = team_info[0].get('venue', {})
            stats = fetch_from_api('teams/statistics', {
                'team': team_id,
                'season': '2024',
                'league': get_league_id(team_name)
            })
            
            team = {
                'id': team_id,
                'name': team_data.get('name', team_name),
                'logo': team_data.get('logo', ''),
                'country': team_data.get('country', ''),
                'founded': team_data.get('founded', 0),
                'venue_name': venue.get('name', ''),
                'venue_capacity': venue.get('capacity', 0),
                'league': get_league_name(team_name),
                'form': stats.get('form', '') if stats else '',
                'fixtures_played': stats.get('fixtures', {}).get('played', {}).get('total', 0) if stats else 0,
                'wins': stats.get('fixtures', {}).get('wins', {}).get('total', 0) if stats else 0,
                'draws': stats.get('fixtures', {}).get('draws', {}).get('total', 0) if stats else 0,
                'loses': stats.get('fixtures', {}).get('loses', {}).get('total', 0) if stats else 0,
                'goals_for': stats.get('goals', {}).get('for', {}).get('total', {}).get('total', 0) if stats else 0,
                'goals_against': stats.get('goals', {}).get('against', {}).get('total', {}).get('total', 0) if stats else 0,
                'clean_sheets': stats.get('clean_sheet', {}).get('total', 0) if stats else 0
            }
            teams.append(team)
    
    print(f"✓ Totale squadre: {len(teams)}")
    return teams

# ═══════════════════════════════════════════
# NEWS RSS
# ═══════════════════════════════════════════
def classify_news(title):
    title_lower = title.lower()
    official_keywords = ['ufficiale', 'official', 'confirmed', 'announced', 'here we go', 'firmato', 'contratto', 'ingaggio', 'presentato', 'depositato', 'tesserato']
    negotiation_keywords = ['trattativa', 'accordo', 'intesa', 'vicino', 'contatto', 'offerta', 'rinnovo', 'prolunga', 'in talks', 'deal', 'bid', 'offer']
    
    for word in official_keywords:
        if word in title_lower:
            return 'Official', 95
    for word in negotiation_keywords:
        if word in title_lower:
            return 'Negotiation', 85
    return 'Rumor', 70

def detect_league(title):
    title_lower = title.lower()
    league_teams = {
        'Premier League': ['arsenal', 'chelsea', 'liverpool', 'man city', 'manchester city', 'man utd', 'manchester united', 'tottenham'],
        'Serie A': ['juventus', 'inter', 'milan', 'ac milan', 'napoli', 'roma', 'lazio'],
        'La Liga': ['real madrid', 'barcelona', 'barcellona', 'atletico madrid'],
        'Bundesliga': ['bayern', 'borussia dortmund', 'dortmund', 'leverkusen'],
        'Ligue 1': ['psg', 'paris saint-germain', 'marseille', 'lyon', 'monaco']
    }
    for league, teams in league_teams.items():
        for team in teams:
            if team in title_lower:
                return league
    return None

def fetch_news():
    print("\n📰 Scaricamento news RSS...")
    all_news = []
    
    # Carica news esistenti
    if os.path.exists('news.json'):
        try:
            with open('news.json', 'r', encoding='utf-8') as f:
                all_news = json.load(f)
            print(f"  Caricate {len(all_news)} news esistenti")
        except Exception as e:
            print(f"  Errore caricamento news.json: {e}")
            all_news = []

    existing_links = {item.get('link') for item in all_news if item.get('link')}
    new_count = 0

    for feed_info in FEEDS:
        try:
            feed = feedparser.parse(feed_info['url'])
            print(f"  ✓ {feed_info['name']}: {len(feed.entries)} notizie trovate")
            
            for entry in feed.entries[:5]:
                # CONTROLLO ROBUSTO
                if not hasattr(entry, 'link') or not entry.link:
                    print(f"    ⚠️ News senza link, salto")
                    continue
                
                if not hasattr(entry, 'title') or not entry.title:
                    print(f"    ⚠️ News senza titolo, salto")
                    continue
                
                if entry.link not in existing_links:
                    news_type, reliability = classify_news(entry.title)
                    league = detect_league(entry.title)
                    
                    # Estrai excerpt dal feed
                    excerpt = ''
                    if hasattr(entry, 'summary'):
                        excerpt = entry.summary[:300]
                    elif hasattr(entry, 'description'):
                        excerpt = entry.description[:300]
                    
                    # Scarica riassunto (3 paragrafi, max 800 caratteri)
                    print(f"    📥 Download riassunto...")
                    summary = fetch_article_summary(entry.link, max_paragraphs=3)
                    
                    all_news.append({
                        'id': len(all_news) + 1,
                        'title': entry.title,
                        'link': entry.link,
                        'source': feed_info['name'],
                        'date': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'type': news_type,
                        'reliability': reliability,
                        'league': league,
                        'excerpt': excerpt,
                        'summary': summary  # Riassunto di 3 paragrafi
                    })
                    existing_links.add(entry.link)
                    new_count += 1
                    print(f"    ✅ Aggiunta: {entry.title[:50]}...")
        except Exception as e:
            print(f"  ❌ Errore {feed_info['name']}: {e}")

    # Ordina per data e limita a 50
    all_news.sort(key=lambda x: x['date'], reverse=True)
    all_news = all_news[:50]

    # Salva
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)
    
    print(f"✅ News totali: {len(all_news)}, Nuove: {new_count}")

# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("=" * 50)
    print("🚀 MERCATO MAESTRO - Bot avviato!")
    print("=" * 50)
    
    # DEBUG
    print(f"\n🔍 DEBUG API:")
    print(f"   API_FOOTBALL_KEY in env: {'API_FOOTBALL_KEY' in os.environ}")
    if API_FOOTBALL_KEY:
        print(f"   ✅ Key presente (lunghezza: {len(API_FOOTBALL_KEY)})")
        print(f"   ✅ USE_API_FOOTBALL: {USE_API_FOOTBALL}")
    else:
        print(f"   ❌ Key ASSENTE!")
    print("=" * 50)
    
    # 1. News RSS
    try:
        fetch_news()
    except Exception as e:
        print(f"❌ Errore news: {e}")
    
    # 2. API Football
    if USE_API_FOOTBALL:
        try:
            cache = load_cache()
            
            if not cache:
                print("\n📡 Cache vuota, scaricamento API...")
                players = fetch_players_data()
                teams = fetch_teams_data()
                
                if players:
                    with open('players.json', 'w', encoding='utf-8') as f:
                        json.dump(players, f, indent=2, ensure_ascii=False)
                    print(f"✓ Salvati {len(players)} giocatori")
                
                if teams:
                    with open('teams.json', 'w', encoding='utf-8') as f:
                        json.dump(teams, f, indent=2, ensure_ascii=False)
                    print(f"✓ Salvate {len(teams)} squadre")
                
                if players or teams:
                    save_cache({'players': players, 'teams': teams})
            else:
                print("\n✓ Dati dalla cache")
                players = cache.get('players', [])
                teams = cache.get('teams', [])
                
                if players:
                    with open('players.json', 'w', encoding='utf-8') as f:
                        json.dump(players, f, indent=2, ensure_ascii=False)
                if teams:
                    with open('teams.json', 'w', encoding='utf-8') as f:
                        json.dump(teams, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Errore API: {e}")
    else:
        print("\n⚠️ API-Football NON attivo")
    
    print("\n" + "=" * 50)
    print("✅ Bot completato!")
    print("=" * 50)

if __name__ == "__main__":
    main()
