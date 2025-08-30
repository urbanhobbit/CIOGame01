import streamlit as st
import random
import pandas as pd
import altair as alt
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path

# --- CUSTOM CSS (TECHNO/CYBERPUNK THEME - HIGH CONTRAST LIGHT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;700&display=swap');

    /* General layout and background */
    body, .main { 
        background-color: #f0f2f6; /* Açık gri arka plan */
        color: #2c3e50; /* Koyu metin rengi */
        font-family: 'Rajdhani', sans-serif;
    }

    /* Card-like containers for content */
    .crisis-card {
        background-color: #ffffff; /* Beyaz kart zemini */
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 1rem;
        border: 1px solid #d1d9e6; /* Hafif çerçeve */
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
    }
    .crisis-card:hover {
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.6); /* Camgöbeği parlama */
    }

    /* News Ticker Styling */
    .news-ticker {
        background-color: #2c3e50; /* Koyu ana renk */
        color: #f0f0f0; /* Açık metin */
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-family: 'monospace';
        font-size: 0.95rem;
        border: 1px solid #2c3e50;
    }
    .news-ticker h4 {
        color: #00ffff; /* Camgöbeği başlık */
        margin-bottom: 10px;
        border-bottom: 1px solid #7f8c8d;
        padding-bottom: 5px;
    }
    .news-ticker p {
        margin-bottom: 5px;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(45deg, #00ffff, #ff00ff); /* Camgöbeği-Macenta gradyanı */
        color: #ffffff; /* Beyaz metin */
        border-radius: 8px;
        padding: 12px 28px;
        font-weight: 700; /* Kalın font */
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.8); /* Macenta parlama */
        transform: scale(1.05);
    }
    .stButton>button:disabled {
        background: #cccccc;
        color: #666666;
        box-shadow: none;
    }

    /* Metric styling */
    .metric-positive { color: #2ca02c; font-weight: bold; } /* Yeşil */
    .metric-negative { color: #d62728; font-weight: bold; } /* Kırmızı */

    /* Sidebar styling */
    .st-emotion-cache-16txtl3 {
        background-color: #ffffff;
    }
    .sidebar .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ffff, #ff00ff);
    }
    
    /* Headings and text for readability */
    h1, h2, h3 { 
        color: #1f2937; /* Çok koyu gri */
        font-weight: 700;
    }
    h4, h5 {
        color: #ff00ff; /* Parlak Macenta */
        font-weight: 700;
    }
    small {
        color: #6b7280; /* Orta gri */
    }

    /* Expander styling */
    .st-expander {
        background-color: #fafafa;
        border-radius: 8px;
        border: 1px solid #d1d9e6;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA MODELS ---
# Using dataclasses for structured, readable, and maintainable data definitions.

@dataclass
class ActionCard:
    id: str
    name: str
    cost: int
    hr_cost: int
    speed: str
    security_effect: int
    freedom_cost: int
    side_effect_risk: float
    safeguard_reduction: float
    tooltip: str

@dataclass
class Advisor:
    name: str
    text: str

@dataclass
class Scenario:
    id: str
    title: str
    icon: str
    story: str
    advisors: List[Advisor]
    action_cards: List[ActionCard]
    immediate_text: str
    delayed_text: str

# --- GAME CONTENT & CONFIGURATION ---
# Centralized place for all game scenarios and initial settings.

@st.cache_data
def load_json_data(filepath: str, _cache_bust: float) -> Dict:
    """Loads any JSON file. _cache_bust (e.g., file mtime) invalidates cache when file changes."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Hata: {filepath} dosyası bulunamadı. Lütfen dosyanın mevcut olduğundan emin olun.")
        return None

def get_scenarios() -> Dict[str, Scenario]:
    """Parses scenario data from the loaded JSON into Scenario objects."""
    scenarios_path = (Path(__file__).parent / 'scenarios.json')
    scenarios_data = load_json_data(str(scenarios_path), scenarios_path.stat().st_mtime)
    if not scenarios_data:
        return {}
    
    scenarios = {}
    for key, data in scenarios_data.items():
        # JSON'daki "action_cards" gibi anahtarları kontrol et
        if 'action_cards' in data and 'advisors' in data:
            scenarios[key] = Scenario(
                id=key,
                title=data.get('title', 'Başlıksız Senaryo'),
                icon=data.get('icon', '❓'),
                story=data.get('story', ''),
                advisors=[Advisor(**advisor) for advisor in data['advisors']],
                action_cards=[ActionCard(**card) for card in data['action_cards']],
                immediate_text=data.get('immediate_text', ''),
                delayed_text=data.get('delayed_text', '')
            )
    return scenarios

# --- GAME LOGIC ---
# Core functions that manage game state and calculate outcomes.

def initialize_game_state():
    """Sets up the session state for a new game if it doesn't exist."""
    if 'game_initialized' not in st.session_state:
        cfg_path = (Path(__file__).parent / 'config.json')
        config = load_json_data(str(cfg_path), cfg_path.stat().st_mtime)
        if not config:
            st.stop() # Stop execution if config is not found
        
        settings = config.get('initial_settings', {})
        
        st.session_state.game_initialized = True
        st.session_state.screen = 'start_game'
        st.session_state.metrics = settings.get('metrics', {}).copy()
        st.session_state.budget = settings.get('budget', 100)
        st.session_state.human_resources = settings.get('hr', 50)
        st.session_state.max_crises = settings.get('max_crises', 3)
        st.session_state.crisis_history = []
        st.session_state.news_ticker = ["Oyun başladı. Ülke durumu stabil."]
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_sequence = []
        st.session_state.selected_scenario_id = None
        st.session_state.decision = {}
        st.session_state.results = None
        st.session_state.config = config # Store config in session state

def reset_game():
    """Resets the game to its initial state."""
    st.session_state.game_initialized = False
    initialize_game_state()
    st.rerun()

def add_news(headline):
    """Adds a new headline to the news ticker."""
    st.session_state.news_ticker.insert(0, headline)
    if len(st.session_state.news_ticker) > 5:
        st.session_state.news_ticker.pop()

def calculate_effects(action: ActionCard, scope: str, duration: str, safeguards: List[str]) -> Dict:
    """Calculates the effects of a player's decision on the game metrics."""
    # --- Load balance parameters from config ---
    balance = st.session_state.config['game_balance']
    
    THREAT_SEVERITY = balance['THREAT_SEVERITY']
    RANDOM_FACTOR_RANGE = tuple(balance['RANDOM_FACTOR_RANGE'])
    SCOPE_MULTIPLIERS = balance['SCOPE_MULTIPLIERS']
    DURATION_MULTIPLIERS = balance['DURATION_MULTIPLIERS']
    SAFEGUARD_QUALITY_PER_ITEM = balance['SAFEGUARD_QUALITY_PER_ITEM']
    TRUST_BOOST_FOR_TRANSPARENCY = balance['TRUST_BOOST_FOR_TRANSPARENCY']
    FATIGUE_PER_DURATION = balance['FATIGUE_PER_DURATION']

    # --- Calculation logic (unchanged, but now uses variables from config) ---
    random_factor = random.uniform(*RANDOM_FACTOR_RANGE)
    scope_multiplier = SCOPE_MULTIPLIERS[scope]
    duration_multiplier = DURATION_MULTIPLIERS[duration]
    safeguard_quality = len(safeguards) * SAFEGUARD_QUALITY_PER_ITEM

    security_change = (THREAT_SEVERITY * action.security_effect / 100) - (action.side_effect_risk * random_factor * 20)
    freedom_cost = action.freedom_cost * scope_multiplier * duration_multiplier * (1 - safeguard_quality * action.safeguard_reduction)
    public_trust_change = (TRUST_BOOST_FOR_TRANSPARENCY if 'transparency' in safeguards else 0) - (freedom_cost * 0.5)
    resilience_change = (action.security_effect * safeguard_quality / 2) if action.speed == 'slow' else 5
    fatigue_change = duration_multiplier * FATIGUE_PER_DURATION[scope]

    # --- News Ticker Logic ---
    if security_change > 15:
        add_news(f"📈 GÜVENLİK ARTTI: '{action.name}' politikası sonrası tehdit seviyesi düştü.")
    if freedom_cost > 15:
        add_news(f"📉 ÖZGÜRLÜK TARTIŞMASI: Yeni kısıtlamalar sivil toplumdan tepki çekti.")
    if 'transparency' in safeguards:
        add_news("📰 ŞEFFAFLIK ADIMI: Hükümet, atılan adımlarla ilgili detaylı rapor yayınladı.")

    # --- Counter-factual analysis text ---
    if action.id == 'A':
        counter_factual = 'B veya C ile aynı güvenliğe daha düşük özgürlük maliyetiyle ulaşabilirdiniz.'
    else:
        counter_factual = 'Bu, orantılı bir seçimdi; güvenceler fark yarattı.'

    return {
        'security': min(100, max(0, st.session_state.metrics['security'] + security_change)),
        'freedom': min(100, max(0, st.session_state.metrics['freedom'] - freedom_cost)),
        'public_trust': min(100, max(0, st.session_state.metrics['public_trust'] + public_trust_change)),
        'resilience': min(100, max(0, st.session_state.metrics['resilience'] + resilience_change)),
        'fatigue': min(100, max(0, st.session_state.metrics['fatigue'] + fatigue_change)),
        'counter_factual': counter_factual,
        'budget': st.session_state.budget - action.cost,
        'human_resources': st.session_state.human_resources - action.hr_cost
    }

def calculate_skip_turn_effects():
    """Calculates the negative effects of skipping a turn due to lack of resources."""
    add_news("🚨 KAYNAK YETERSİZ: Hükümet, kaynak yetersizliği nedeniyle krize müdahale edemedi.")
    
    security_penalty = -25
    trust_penalty = -20
    resilience_penalty = -10
    fatigue_increase = 15
    counter_factual = "Kaynaklarınızı daha verimli kullanmış olsaydınız, bu krize müdahale edebilir ve daha büyük zararları önleyebilirdiniz."

    return {
        'security': min(100, max(0, st.session_state.metrics['security'] + security_penalty)),
        'freedom': st.session_state.metrics['freedom'],
        'public_trust': min(100, max(0, st.session_state.metrics['public_trust'] + trust_penalty)),
        'resilience': min(100, max(0, st.session_state.metrics['resilience'] + resilience_penalty)),
        'fatigue': min(100, max(0, st.session_state.metrics['fatigue'] + fatigue_increase)),
        'counter_factual': counter_factual,
        'budget': st.session_state.budget,
        'human_resources': st.session_state.human_resources
    }

# --- UI COMPONENTS ---
# Reusable functions for rendering parts of the UI.

def display_metrics_sidebar():
    """Displays the main status dashboard in the sidebar."""
    st.sidebar.header("📊 Durum Panosu")
    
    # Show current crisis count
    if 'crisis_sequence' in st.session_state and st.session_state.crisis_sequence and st.session_state.screen != 'game_end':
        st.sidebar.markdown(f"### KRİZ {st.session_state.current_crisis_index + 1} / {len(st.session_state.crisis_sequence)}")

    settings = st.session_state.config['initial_settings']
    INITIAL_BUDGET = settings['budget']
    INITIAL_HR = settings['hr']
    
    metrics_data = [
        ('💰 Bütçe', st.session_state.budget, INITIAL_BUDGET),
        ('👥 İnsan Kaynağı', st.session_state.human_resources, INITIAL_HR),
        ('🛡️ Güvenlik', st.session_state.metrics['security'], 100),
        ('🗽 Özgürlük', st.session_state.metrics['freedom'], 100),
        ('🤝 Kamu Güveni', st.session_state.metrics['public_trust'], 100),
        ('💪 Dayanıklılık', st.session_state.metrics['resilience'], 100),
        ('😩 Uyum Yorgunluğu', st.session_state.metrics['fatigue'], 100)
    ]
    for name, value, max_value in metrics_data:
        st.sidebar.markdown(f"**{name}**")
        st.sidebar.progress(min(max(value / max_value, 0), 1))
        st.sidebar.markdown(f"<div style='text-align: right;'>{value:.1f} / {max_value}</div>", unsafe_allow_html=True)
    
    st.sidebar.write("---")
    if st.session_state.screen not in ['start_game', 'game_end']:
        if st.sidebar.button("Oyunu Bitir"):
            if not st.session_state.results:
                st.session_state.results = st.session_state.metrics
            st.session_state.screen = 'game_end'
            st.rerun()

def display_help_guide():
    """Displays the collapsible help guide."""
    with st.expander("Yardım: Oyun Rehberi"):
        st.markdown("""
            - **Amaç**: Krizleri yönetirken güvenlik ve özgürlük arasında denge kurun.
            - **Metrikler**: Güvenlik, Özgürlük, Kamu Güveni, Dayanıklılık ve Uyum Yorgunluğu’nu izleyin.
            - **Kararlar**: Aksiyonları seçin, kapsam/süre/güvenceleri ayarlayın.
            - **Güvenceler**: Şeffaflık, itiraz mekanizması ve otomatik sona erdirme, özgürlük kaybını azaltır.
            - **Riskler**: Geniş kapsam veya uzun süre, özgürlük ve meşruiyeti zedeler. Uyum yorgunluğu 50’yi aşarsa meşruiyet krizi riski artar.
            **İpucu**: Hedefli ve güvenceli önlemler, uzun vadede daha sürdürülebilir!
        """)

def display_guidance(text: str):
    """Displays a styled guidance box."""
    st.markdown(f"""
    <div class="crisis-card" style="background-color: #e8f0fe; border-left: 5px solid #00ffff;">
        💡 <strong>Rehber</strong>: {text}
    </div>
    """, unsafe_allow_html=True)

def display_news_ticker():
    """Displays the news ticker with recent headlines."""
    st.markdown('<div class="news-ticker"><h4>Haber Akışı</h4>', unsafe_allow_html=True)
    for news_item in st.session_state.news_ticker:
        st.markdown(f"<p>• {news_item}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def format_advisor_text(text: str) -> str:
    """Formats advisor text to highlight pros and cons with colors."""
    if '✅' in text:
        main_part, pro_con_part = text.split('✅', 1)
        if '❌' in pro_con_part:
            pro_part, con_part = pro_con_part.split('❌', 1)
            return f"{main_part}<br>✅<strong style='color:green;'>{pro_part.strip()}</strong><br>❌<strong style='color:red;'>{con_part.strip()}</strong>"
        else:
            return f"{main_part}<br>✅<strong style='color:green;'>{pro_con_part.strip()}</strong>"
    return text

# --- SCREEN RENDERERS ---
# Functions responsible for drawing each screen of the game.

def start_game_screen():
    st.title("🛡️ CIO Kriz Yönetimi Oyunu")
    st.markdown("""
        <div class="crisis-card">
            <h2>Hoş Geldin!</h2>
            <p>.... adasının bilgi şefi sensin! Burası sakin ve huzurlu bir ada… ama son zamanlarda depremden sele, yangından siber saldırıya kadar krizler peşini bırakmıyor.</p>
            <p>Senin görevin, halkın doğru bilgiye ulaşmasını sağlamak ve yanlış bilgileri engellemek. Fakat bunu yaparken halkın haklarını veya özgürlüğünü kısıtlamadan yapmaya çalışmak zorundasın.</p>
            <p>Her kriz kartında sana farklı danışmanlar yol gösterecek, onların önerilerini dikkatle dinle ve ardından 3 aksiyon kartından birini seç. Seçimin, adanın Bütçe, İnsan Kaynağı, Güvenlik, Özgürlük, Kamu Güveni, Dayanıklılık ve Uyum Yorgunluğu değerlerini etkiler.</p>
            <p><b>Amaç:</b> krizleri yönetirken adalıların hem güvenliğini hem özgürlüğünü korumak!<br>Bakalım adayı hem güvenli hem özgür tutabilecek bir lider misin?</p>
        </div>
    """, unsafe_allow_html=True)
    
    scenarios = get_scenarios()
    keys = list(scenarios.keys())
    if not keys:
        st.warning('Hiç senaryo bulunamadı. Lütfen editörden en az bir senaryo ekleyin ve tekrar deneyin.')
        return
    selected = st.multiselect('Bu oyunda oynanacak senaryolar:', options=keys, default=keys, help='Listeyi daraltarak yeni eklediğiniz senaryonun seçildiğinden emin olun.')
    if st.button('Oyunu Başlat'):
        crisis_keys = selected or keys
        if not crisis_keys:
            st.warning('Başlamak için en az bir senaryo seçin.')
            return
        random.shuffle(crisis_keys)
        st.session_state.crisis_sequence = crisis_keys[:st.session_state.max_crises]
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_history.append(st.session_state.metrics.copy())
        st.session_state.selected_scenario_id = st.session_state.crisis_sequence[0]
        st.session_state.screen = 'story'
        st.rerun()

def story_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title(f"{scenario.icon} Kriz {st.session_state.current_crisis_index + 1}: {scenario.title}")

    try:
        report_part, mission_part = scenario.story.split("**Görev**:")
    except ValueError:
        report_part = scenario.story
        mission_part = ""

    st.markdown(f'<div class="crisis-card">{report_part}</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="crisis-card" style="border-left: 5px solid #ff00ff;">
            <h4>Görev</h4><hr><p>{mission_part}</p>
        </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    display_guidance("Kararlarınız can güvenliğini artırabilir, ancak özgürlükleri ve halkın güvenini etkileyebilir. Dengeyi bulmaya hazır mısınız?")
    
    if st.button("Danışmanları Dinle"):
        st.session_state.screen = 'advisors'
        st.rerun()

def advisors_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title("Danışman Görüşleri")
    display_news_ticker()

    cols = st.columns(len(scenario.advisors))
    for i, advisor in enumerate(scenario.advisors):
        with cols[i]:
            formatted_text = format_advisor_text(advisor.text)
            st.markdown(f"""
            <div class="crisis-card">
                <h5>{advisor.name}</h5><hr><p>{formatted_text}</p>
            </div>
            """, unsafe_allow_html=True)

    display_guidance("Her danışmanın önerisi farklı bir strateji sunuyor. Önyargılarına dikkat edin ve uzun vadeli etkileri düşünün!")

    if st.button("Karar Aşamasına Geç"):
        st.session_state.screen = 'decision'
        st.rerun()

def decision_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title("Karar Paneli")
    display_news_ticker()

    st.markdown(f"""
        <div class="crisis-card">
            <h3>Kaynaklar</h3>
            <p><strong>Mevcut Bütçe</strong>: {st.session_state.budget} | <strong>İnsan Kaynağı</strong>: {st.session_state.human_resources}</p>
        </div>
    """, unsafe_allow_html=True)

    affordable_actions = [card for card in scenario.action_cards if st.session_state.budget >= card.cost and st.session_state.human_resources >= card.hr_cost]

    if not affordable_actions:
        st.warning("Kaynaklarınız yetersiz! Hiçbir politikayı uygulayacak bütçeniz veya insan kaynağınız kalmadı.")
        if st.button("Turu Atla (Negatif Sonuçlar Doğurur)"):
            results = calculate_skip_turn_effects()
            st.session_state.results = results
            st.session_state.decision = {'action': 'SKIP', 'skipped': True}
            st.session_state.screen = 'immediate'
            st.rerun()
    else:
        st.subheader("Aksiyon Seç")
        cols = st.columns(len(scenario.action_cards))
        selected_action_id = st.session_state.decision.get('action')

        for i, card in enumerate(scenario.action_cards):
            with cols[i]:
                is_affordable = st.session_state.budget >= card.cost and st.session_state.human_resources >= card.hr_cost
                is_selected = selected_action_id == card.id
                border_style = "border: 2px solid #ff00ff;" if is_selected else "border: 1px solid #d1d9e6;"
                
                st.markdown(f"""
                    <div class="crisis-card" style="{border_style}">
                        <h5>{card.name}</h5><p>{card.tooltip}</p>
                        <small>
                            Maliyet: {card.cost} 💰 | HR: {card.hr_cost} 👥 | Hız: {card.speed.capitalize()}<br>
                            Etki: <span style="color:green;">🛡️ +{card.security_effect}</span> | <span style="color:red;">🗽 -{card.freedom_cost}</span>
                        </small>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Bunu Seç", key=f"select_{card.id}", disabled=not is_affordable):
                    st.session_state.decision['action'] = card.id
                    st.rerun()
        
        if selected_action_id:
            st.subheader("Politika Ayarları")
            with st.container(border=False):
                st.markdown('<div class="crisis-card">', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    scope = st.radio("Kapsam:", ["Hedefli", "Genel"], key="scope")
                with c2:
                    duration = st.radio("Süre:", ["Kısa", "Orta", "Uzun"], key="duration")
                
                st.subheader("Güvenceler")
                safeguards = []
                if st.checkbox("🛡️ Şeffaflık Raporu (Kamu güvenini artırır, özgürlük kaybını azaltır)"): safeguards.append("transparency")
                if st.checkbox("⚖️ İtiraz Mekanizması (Hatalı kararları düzeltme şansı sunar)"): safeguards.append("appeal")
                if st.checkbox("⏳ Otomatik Sona Erdirme (Normalleşme kaymasını önler)"): safeguards.append("sunset")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Uygula"):
                action = next(card for card in scenario.action_cards if card.id == selected_action_id)
                
                st.session_state.decision.update({
                    'scope': 'targeted' if scope == "Hedefli" else 'general',
                    'duration': {'Kısa': 'short', 'Orta': 'medium', 'Uzun': 'long'}[duration],
                    'safeguards': safeguards,
                    'skipped': False
                })
                results = calculate_effects(action, st.session_state.decision['scope'], st.session_state.decision['duration'], safeguards)
                st.session_state.results = results
                st.session_state.budget = results['budget']
                st.session_state.human_resources = results['human_resources']
                st.session_state.screen = 'immediate'
                st.rerun()

def immediate_screen():
    results = st.session_state.results
    old_metrics = st.session_state.crisis_history[st.session_state.current_crisis_index]
    scenario = get_scenarios()[st.session_state.selected_scenario_id]

    st.title("Anında Etki")
    display_news_ticker()

    if st.session_state.decision.get('skipped'):
        immediate_text = "Kaynak yetersizliği nedeniyle hükümet krize müdahale edemedi. Bu durum, krizin etkilerini derinleştirdi ve halk arasında endişeye yol açtı."
        st.markdown(f'<div class="crisis-card"><h3>Olay Günlüğü</h3><p>{immediate_text}</p></div>', unsafe_allow_html=True)
    else:
        action = next(card for card in scenario.action_cards if card.id == st.session_state.decision['action'])
        immediate_text = scenario.immediate_text.format(f"<b>{action.name}</b>")
        
        st.markdown(f'<div class="crisis-card"><h3>Olay Günlüğü</h3><p>{immediate_text}</p></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            old_budget = results['budget'] + action.cost
            old_hr = results['human_resources'] + action.hr_cost
            st.markdown(f"""
            <div class="crisis-card" style="height: 100%;">
                <h4>💰 Kaynaklardaki Değişim</h4><hr>
                <ul>
                    <li><strong>Bütçe</strong>: {old_budget:.0f} ➡️ <span class="metric-negative">{results['budget']:.0f}</span> (-{action.cost})</li>
                    <li><strong>İnsan Kaynağı</strong>: {old_hr:.0f} ➡️ <span class="metric-negative">{results['human_resources']:.0f}</span> (-{action.hr_cost})</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="crisis-card" style="height: 100%;">
                <h4>📊 Metriklerdeki Değişim</h4><hr>
                <ul>
                    <li><strong>Güvenlik</strong>: {old_metrics['security']:.1f} ➡️ <span class="{'metric-positive' if results['security'] > old_metrics['security'] else 'metric-negative'}">{results['security']:.1f}</span> ({results['security'] - old_metrics['security']:+.1f})</li>
                    <li><strong>Özgürlük</strong>: {old_metrics['freedom']:.1f} ➡️ <span class="{'metric-positive' if results['freedom'] > old_metrics['freedom'] else 'metric-negative'}">{results['freedom']:.1f}</span> ({results['freedom'] - old_metrics['freedom']:+.1f})</li>
                    <li><strong>Kamu Güveni</strong>: {old_metrics['public_trust']:.1f} ➡️ <span class="{'metric-positive' if results['public_trust'] > old_metrics['public_trust'] else 'metric-negative'}">{results['public_trust']:.1f}</span> ({results['public_trust'] - old_metrics['public_trust']:+.1f})</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Bir Süre Sonra..."):
        st.session_state.screen = 'delayed'
        st.rerun()

def delayed_screen():
    current_results = st.session_state.results
    delayed_results = {
        **current_results,
        'security': min(100, current_results['security'] + (10 if st.session_state.decision.get('action') == 'C' else 5)),
        'resilience': min(100, current_results['resilience'] + (10 if st.session_state.decision.get('action') == 'C' else 5)),
        'public_trust': min(100, max(0, current_results['public_trust'] - (3 if random.random() > 0.7 else 0)))
    }
    st.session_state.results = delayed_results

    st.title("Gecikmeli Etkiler")
    display_news_ticker()

    if st.session_state.decision.get('skipped'):
        delayed_text = "Eylemsizliğin uzun vadeli sonuçları ağır oldu. Toparlanma süreci yavaşlarken, gelecekteki krizlere karşı ülkenin dayanıklılığı ciddi şekilde azaldı."
    else:
        scenario = get_scenarios()[st.session_state.selected_scenario_id]
        delayed_text = scenario.delayed_text

    st.markdown(f"""
        <div class="crisis-card">
            <h3>Olay Günlüğü</h3><p>{delayed_text}</p>
            <h4>Uzun Vadeli Etkiler</h4>
            <ul>
                <li><strong>Dayanıklılık</strong>: <span class="{'metric-positive' if delayed_results['resilience'] > current_results['resilience'] else 'metric-negative'}">{delayed_results['resilience']:.1f}</span> – Eğitim gelecek krizlere hazırladı.</li>
                <li><strong>Uyum Yorgunluğu</strong>: <span class="{'metric-positive' if delayed_results['fatigue'] < current_results['fatigue'] else 'metric-negative'}">{delayed_results['fatigue']:.1f}</span> – Uzun süreli önlemler tepkiyi zorlaştırabilir.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    display_guidance("Dayanıklılık, gelecek krizlerde otomatik güvenlik artışı sağlar. Uyum yorgunluğu 50’yi aşarsa, meşruiyet krizi riski artar.")

    if st.button("Raporu Gör"):
        st.session_state.screen = 'report'
        st.rerun()

def report_screen():
    st.session_state.metrics = st.session_state.results.copy()
    st.title(f"Kriz {st.session_state.current_crisis_index + 1} Sonu Raporu")
    
    st.markdown('<div class="crisis-card"><h3>Sonuçlar</h3>', unsafe_allow_html=True)
    previous_metrics = st.session_state.crisis_history[st.session_state.current_crisis_index]
    current_metrics = st.session_state.metrics

    df = pd.DataFrame([
        {'Gösterge': 'Güvenlik', 'Başlangıç': previous_metrics['security'], 'Son': current_metrics['security']},
        {'Gösterge': 'Özgürlük', 'Başlangıç': previous_metrics['freedom'], 'Son': current_metrics['freedom']},
        {'Gösterge': 'Kamu Güveni', 'Başlangıç': previous_metrics['public_trust'], 'Son': current_metrics['public_trust']},
        {'Gösterge': 'Dayanıklılık', 'Başlangıç': previous_metrics['resilience'], 'Son': current_metrics['resilience']},
        {'Gösterge': 'Uyum Yorgunluğu', 'Başlangıç': previous_metrics['fatigue'], 'Son': current_metrics['fatigue']}
    ])
    
    report_df_melted = df.melt(id_vars=['Gösterge'], value_vars=['Başlangıç', 'Son'], var_name='Durum', value_name='Değer')
    
    bar_chart = alt.Chart(report_df_melted).mark_bar().encode(
        x=alt.X('Durum:N', title=None, axis=alt.Axis(labels=True, ticks=False, domain=False)),
        y=alt.Y('Değer:Q', title='Puan', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Durum:N', title='Durum', scale=alt.Scale(domain=['Başlangıç', 'Son'], range=['#00ffff', '#ff00ff'])),
        column=alt.Column('Gösterge:N', title='Metrikler', header=alt.Header(labelOrient='bottom', titleOrient='bottom'))
    ).properties(width=alt.Step(40), title='Metriklerin Başlangıç ve Son Değerleri').configure_title(fontSize=16, anchor='middle').configure_view(stroke=None)
    
    st.altair_chart(bar_chart, use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="crisis-card">
            <h3>📊 Karşı-Olgu Analizi</h3>
            <p><i>{st.session_state.results['counter_factual']}</i></p>
            <p><strong>Analiz:</strong> Geniş kapsam veya uzun süre, ifade ve mahremiyeti etkiledi. Seçtiğiniz <strong>{len(st.session_state.decision.get('safeguards', []))} güvence</strong>, özgürlük kaybını yaklaşık %{len(st.session_state.decision.get('safeguards', [])) * 15} oranında azalttı.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="crisis-card">
            <h3>🔗 Gerçek Dünya Bağlantısı</h3>
            <p>Kararlarınız, gerçek dünyadaki yönetişim ilkeleriyle örtüşüyor:</p>
            <ul>
                <li><strong>Gerekli ve Orantılı Olma</strong>: AB Veri Koruma Kuralları (GDPR) gibi düzenlemeler, müdahalelerin hedefe yönelik ve orantılı olmasını vurgular.</li>
                <li><strong>Şeffaflık</strong>: Google gibi şirketlerin şeffaflık raporları, halkın güvenini artırmada kritik bir rol oynar.</li>
                <li><strong>Normalleşme Kayması</strong>: Acil durum yetkilerinin kalıcı hale gelmesi, demokratik toplumlar için bir risktir. Otomatik sona erdirme (sunset) maddeleri bu riski azaltır.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sonraki Krize Geç"):
        st.session_state.current_crisis_index += 1
        st.session_state.crisis_history.append(st.session_state.metrics.copy())

        if st.session_state.current_crisis_index < len(st.session_state.crisis_sequence):
            st.session_state.selected_scenario_id = st.session_state.crisis_sequence[st.session_state.current_crisis_index]
            st.session_state.decision = {}
            st.session_state.screen = 'story'
        else:
            st.session_state.screen = 'game_end'
        st.rerun()

def game_end_screen():
    st.title("🏆 Oyun Sonu: Krizler Tarihi")
    st.balloons()
    
    final_metrics = st.session_state.results
    leadership_score = (final_metrics['security'] + final_metrics['freedom'] + final_metrics['public_trust']) / 3
    
    if leadership_score > 75: score_text = 'Mükemmel! Güvenlik, özgürlük ve kamu güvenini dengede tuttunuz.'
    elif leadership_score > 55: score_text = 'İyi iş, ama bazı alanlarda daha az maliyetli yollar mümkündü.'
    else: score_text = 'Zorlu bir yolculuktu. Daha fazla güvence ve hedefli önlem deneyin.'

    leadership_style = "Dengeli Stratejist"
    style_description = "Kararlarınızda güvenlik, özgürlük ve kamu güveni arasında bir denge kurmaya çalıştınız."
    if final_metrics['security'] > 75 and final_metrics['freedom'] < 50:
        leadership_style = "Otoriter Taktisyen"
        style_description = "Kriz anlarında güvenliği her şeyin önünde tuttunuz, ancak bu durum özgürlükler üzerinde baskı yarattı."
    elif final_metrics['freedom'] > 75 and final_metrics['security'] < 50:
        leadership_style = "Özgürlük Şampiyonu"
        style_description = "Bireysel özgürlükleri ve sivil hakları korumayı önceliklendirdiniz, ancak bu bazen güvenlik metriklerinden ödün vermenize neden oldu."
    elif final_metrics['public_trust'] > 70 and final_metrics['resilience'] > 60:
        leadership_style = "Toplum İnşaatçısı"
        style_description = "Halkın güvenini kazanmaya ve uzun vadeli dayanıklılık oluşturmaya odaklandınız. Bu, sürdürülebilir bir yönetim anlayışını yansıtıyor."

    st.markdown(f"""
        <div class="crisis-card">
            <h3>Liderlik Performansınız</h3>
            <h2>Liderlik Skoru: {leadership_score:.1f}/100</h2>
            <p><i>{score_text}</i></p><hr>
            <h4>Liderlik Tarzınız: {leadership_style}</h4>
            <p>{style_description}</p>
        </div>
    """, unsafe_allow_html=True)

    history_df = pd.DataFrame(st.session_state.crisis_history)
    history_df['Kriz'] = [f"Kriz {i+1} Başlangıcı" for i in range(len(history_df))]
    history_df.loc[0, 'Kriz'] = "Oyun Başlangıcı"
    
    history_df = history_df.melt(id_vars=['Kriz'], var_name='Gösterge', value_name='Değer')
    metric_map = {'security': 'Güvenlik', 'freedom': 'Özgürlük', 'public_trust': 'Kamu Güveni', 'resilience': 'Dayanıklılık', 'fatigue': 'Uyum Yorgunluğu'}
    history_df = history_df[history_df['Gösterge'].isin(metric_map.keys())]
    history_df['Gösterge'] = history_df['Gösterge'].replace(metric_map)
    
    line_chart = alt.Chart(history_df).mark_line(point=True).encode(
        x=alt.X('Kriz:O', sort=None, title='Aşama'),
        y=alt.Y('Değer:Q', title='Puan', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Gösterge:N', title='Metrikler', scale=alt.Scale(scheme='viridis')),
        tooltip=['Kriz', 'Gösterge', alt.Tooltip('Değer:Q', format='.1f')]
    ).properties(title='Krizler Boyunca Metrik Değişimleri', height=400).configure_title(fontSize=16, anchor='middle').configure_view(stroke=None)
    
    st.altair_chart(line_chart, use_container_width=True)

    if st.button("Yeni Oyun Başlat"):
        reset_game()

# --- MAIN APPLICATION FLOW ---
initialize_game_state()
display_metrics_sidebar()

screen_functions = {
    'start_game': start_game_screen,
    'story': story_screen,
    'advisors': advisors_screen,
    'decision': decision_screen,
    'immediate': immediate_screen,
    'delayed': delayed_screen,
    'report': report_screen,
    'game_end': game_end_screen,
}

current_screen_func = screen_functions.get(st.session_state.screen)
if current_screen_func:
    current_screen_func()
    display_help_guide()
else:
    st.error("Bir hata oluştu. Oyun yeniden başlatılıyor.")
    reset_game()

