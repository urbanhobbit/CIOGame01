import streamlit as st
import random
import pandas as pd
import altair as alt
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# --- CUSTOM CSS ---
# Custom styles to improve the visual appeal of the application.
st.markdown("""
<style>
    /* General layout and background */
    .main { 
        background-color: #f0f2f6; /* Lighter grey background */
    }

    /* Card-like containers for content */
    .crisis-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #e6e6e6;
        /* Removed fixed height to allow cards to grow with content */
    }

    /* Button styling */
    .stButton>button {
        background-color: #1f77b4; /* Primary blue */
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff7f0e; /* Orange on hover */
    }
    .stButton>button:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    /* Metric styling for positive/negative feedback */
    .metric-positive { color: #2ca02c; font-weight: bold; } /* Green */
    .metric-negative { color: #d62728; font-weight: bold; } /* Red */

    /* Sidebar progress bar styling */
    .sidebar .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Headings and text */
    h1, h2, h3, h4, h5 { 
        color: #2c3e50; /* Dark-blue-grey for text */
        font-family: 'sans-serif';
    }

    /* Expander styling */
    .st-expander {
        background-color: #fafafa;
        border-radius: 8px;
        border: 1px solid #e6e6e6;
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

def get_scenarios() -> Dict[str, Scenario]:
    """Returns a dictionary of all game scenarios, defined with the data models."""
    return {
        'pandemic': Scenario(
            id='pandemic',
            title='Pandemi Krizi',
            icon=' ',
            story="""
                **Durum Raporu: Acil** Ada ülkesinde yeni bir varyant salgını patlak verdi. R(t) 1.5, hastaneler %80 dolu, yoğun bakım üniteleri sınırda.  
                Sosyal medyada "bitkisel tedavi mucizesi" gibi sahte öneriler viral, aşı karşıtlığı %30 arttı.  
                İletişim ağları tıkanık, panik stokçuluğu marketleri vurdu.  
                **Görev**: CIO olarak, bilgi akışını düzenleyin, yanlış bilgiyi kontrol edin ve halk sağlığını korurken özgürlükleri dengeleyin.
            """,
            advisors=[
                Advisor(name='Tuğgeneral Ayhan (Güvenlik)', text='Hız kritik! Genel karantina ve sosyal medya içerik kaldırma hemen uygulanmalı. Trol çiftlikleriyle sahte anlatıları bastırırız. **Risk**: Meşruiyet kaybı, ama kaosu önler.'),
                Advisor(name='Av. Elif (Hukuk/Ombudsman)', text='Geniş kısıtlamalar mahremiyeti ve ifade özgürlüğünü çökertir. Hedefli izleme ve şeffaflık şart. **Risk**: Yavaş hareket, ama meşruiyet korur.'),
                Advisor(name='Dr. Mert (Siyasi Danışman)', text='Halk panikte, şeffaf iletişim güven artırır. Prebunking ve fact-check kampanyalarıyla anlatıyı yönlendirin. **Risk**: Etki zaman alır.'),
                Advisor(name='Zeynep, CTO (Teknik)', text='Decentralized izleme ve platformlarla MoU en verimli yol. Kendi acil platformumuzu devreye alalım, ama bağımsız yönetim şart. **Risk**: Teknik karmaşa.')
            ],
            action_cards=[
                ActionCard(id='A', name='Merkezi İzleme + Geniş Kaldırma + Karantina', cost=50, hr_cost=20, speed='fast', security_effect=40, freedom_cost=30, side_effect_risk=0.4, safeguard_reduction=0.5, tooltip='Hızlı ama özgürlük maliyeti yüksek. Meşruiyet riski var.'),
                ActionCard(id='B', name='Hedefli İzleme + Platform MoU + Yerel Kısıtlama', cost=30, hr_cost=15, speed='medium', security_effect=30, freedom_cost=15, side_effect_risk=0.2, safeguard_reduction=0.7, tooltip='Dengeli bir seçenek, güvencelerle daha etkili.'),
                ActionCard(id='C', name='Prebunking + Okuryazarlık + Fact-Check + Uzman Paneli', cost=20, hr_cost=10, speed='slow', security_effect=20, freedom_cost=5, side_effect_risk=0.1, safeguard_reduction=0.8, tooltip='Yavaş ama sürdürülebilir, özgürlük dostu.')
            ],
            immediate_text="Seçiminiz devreye girdi: {}. Hastane doluluğu %20 düştü, ancak bazı vatandaşlar 'gizli izleme' iddialarıyla sosyal medyada tepki gösterdi. Medya, kararınızı tartışıyor.",
            delayed_text="""
                **Olay Günlüğü: Bir Hafta Sonra** Yanlış bilgi yayılımı %40 azaldı, ancak bir yanlış kaldırma davası açıldı.  
                Uluslararası sağlık örgütleri kararınızı 'orantılı' buldu, ama halkın bir kısmı şeffaflık talep ediyor.  
                **Not**: Güvenceler, özgürlük kaybını azalttı mı? Uzun vadeli etkiler dayanıklılığı nasıl etkiler?
            """
        ),
        'forest_fire': Scenario(
            id='forest_fire',
            title='Orman Yangınları Krizi',
            icon='🔥',
            story="""
                **Durum Raporu: Kritik** Ada ülkesinin güneyindeki ormanlar alevler içinde, rüzgâr yönü değişiyor. Sahte tahliye haritaları sosyal medyada yayılıyor, iletişim ağları aşırı yükte.  
                Halk panikte, yanlış yönlendirmeler tahliyeyi zorlaştırıyor.  
                **Görev**: CIO olarak, acil iletişim kanallarını açın, yanlış bilgiyi durdurun ve can güvenliğini özgürlüklerle dengeleyin.
            """,
            advisors=[
                Advisor(name='Tuğgeneral Ayhan (Güvenlik)', text='Bölge genelinde sosyal medya kısıtlaması şart! Trol çiftlikleriyle doğru tahliye rotalarını duyururuz. **Risk**: Özgürlük kaybı, ama hayat kurtarır.'),
                Advisor(name='Av. Elif (Hukuk/Ombudsman)', text='Geniş kısıtlamalar ifade özgürlüğünü zedeler. Hedefli iletişim ve şeffaflık raporu gerekir. **Risk**: Yavaş etki, ama meşruiyet korur.'),
                Advisor(name='Dr. Mert (Siyasi Danışman)', text='Halkı sakin tutmak için medya okuryazarlığı kampanyası başlatın. Doğrulanmış haritalar güven artırır. **Risk**: Zaman alır.'),
                Advisor(name='Zeynep, CTO (Teknik)', text='Cell-broadcast ve platformlarla MoU ile tahliye bilgisini hızlandırırız. **Risk**: Teknik koordinasyon zorluğu.')
            ],
            action_cards=[
                ActionCard(id='A', name='Bölge Geniş Kısıtlama + Trol Karşı-Anlatı', cost=40, hr_cost=25, speed='fast', security_effect=35, freedom_cost=25, side_effect_risk=0.35, safeguard_reduction=0.6, tooltip='Hızlı ama ifade özgürlüğünü riske atar.'),
                ActionCard(id='B', name='Cell-Broadcast + Zero-Rating Acil Siteler + Platform MoU', cost=25, hr_cost=15, speed='medium', security_effect=30, freedom_cost=10, side_effect_risk=0.15, safeguard_reduction=0.75, tooltip='Orta hızda, özgürlük dostu bir seçenek.'),
                ActionCard(id='C', name='Bağımsız Medya Sahadan Canlı + Fact-Check Hızlı Şerit', cost=15, hr_cost=10, speed='slow', security_effect=25, freedom_cost=5, side_effect_risk=0.1, safeguard_reduction=0.85, tooltip='Yavaş, düşük riskli ve dayanıklılığı artırır.')
            ],
            immediate_text="Seçiminiz devreye girdi: {}. Tahliye işlemleri hızlandı, ancak bazı bölgelerde internet kesintileri şikayetlere yol açtı. Yerel medya, kararınızı sorguluyor.",
            delayed_text="""
                **Olay Günlüğü: Birkaç Gün Sonra** Yangın kontrol altına alındı, sahte haritaların etkisi %50 azaldı.  
                Ancak, bazı vatandaşlar iletişim kısıtlamalarından şikayetçi. Uluslararası yardım ekipleri kararınızı 'etkili' buldu.  
                **Not**: Şeffaflık, halkın güvenini nasıl etkiledi? Dayanıklılık gelecek krizlerde ne kadar önemli?
            """
        ),
        'earthquake': Scenario(
            id='earthquake',
            title='Deprem Krizi',
            icon='🌍',
            story="""
                **Durum Raporu: Acil** Ada ülkesinde 7.2 büyüklüğünde bir deprem vurdu. Baz istasyonlarının %40’ı devre dışı, “yağma” söylentileri sosyal medyada yayılıyor, yardım koordinasyonu aksıyor.  
                Halk korku içinde, yanlış bilgiler arama-kurtarma çalışmalarını zorlaştırıyor.  
                **Görev**: CIO olarak, iletişim ağlarını restore edin, yanlış bilgiyi kontrol edin ve can güvenliğini özgürlüklerle dengeleyin.
            """,
            advisors=[
                Advisor(name='Tuğgeneral Ayhan (Güvenlik)', text='Ülke çapı içerik yavaşlatma ve geniş gözetim hemen uygulanmalı! **Risk**: Özgürlük kaybı, ama kaosu önler.'),
                Advisor(name='Av. Elif (Hukuk/Ombudsman)', text='Hedefli trafik önceliği ve şeffaflık raporu şart. Geniş gözetim mahremiyeti zedeler. **Risk**: Yavaş etki.'),
                Advisor(name='Dr. Mert (Siyasi Danışman)', text='Halkın güvenini kazanmak için fact-check şeridi ve açık veri panosu kullanın. **Risk**: Organizasyon zaman alır.'),
                Advisor(name='Zeynep, CTO (Teknik)', text='Cell-broadcast ve platformlarla MoU ile yardım koordinasyonunu hızlandırırız. **Risk**: Teknik altyapı sınırlı.')
            ],
            action_cards=[
                ActionCard(id='A', name='Ülke Çapı İçerik Yavaşlatma + Geniş Gözetim', cost=45, hr_cost=30, speed='fast', security_effect=45, freedom_cost=35, side_effect_risk=0.45, safeguard_reduction=0.5, tooltip='Hızlı ama yüksek özgürlük maliyeti.'),
                ActionCard(id='B', name='Hedefli Trafik Önceliği + Platform MoU + Doğrulanmış Yardım Noktaları', cost=35, hr_cost=20, speed='medium', security_effect=35, freedom_cost=15, side_effect_risk=0.25, safeguard_reduction=0.7, tooltip='Dengeli, güvencelerle daha etkili.'),
                ActionCard(id='C', name='Bağımsız Medya Hasar Doğrulama + Açık Veri Panosu', cost=25, hr_cost=15, speed='slow', security_effect=30, freedom_cost=10, side_effect_risk=0.15, safeguard_reduction=0.8, tooltip='Yavaş ama özgürlük dostu ve dayanıklı.')
            ],
            immediate_text="Seçiminiz devreye girdi: {}. Arama-kurtarma ekipleri koordinasyonu %30 iyileşti, ancak bazı kullanıcılar internet erişim sorunu bildirdi. Medya, kararınızı tartışıyor.",
            delayed_text="""
                **Olay Günlüğü: Birkaç Gün Sonra** Yağma söylentileri %60 azaldı, yardım dağıtımı verimli hale geldi.  
                Ancak, bazı vatandaşlar gözetimden rahatsız. Uluslararası kurtarma ekipleri kararınızı 'etkili' buldu.  
                **Not**: Güvenceler meşruiyeti nasıl etkiledi? Dayanıklılık gelecekte ne kadar kritik?
            """
        )
    }

INITIAL_METRICS = {
    'security': 40, 'freedom': 70, 'public_trust': 50, 'resilience': 30, 'fatigue': 10
}
INITIAL_BUDGET = 100
INITIAL_HR = 50
MAX_CRISES = 3

# --- GAME LOGIC ---
# Core functions that manage game state and calculate outcomes.

def initialize_game_state():
    """Sets up the session state for a new game if it doesn't exist."""
    if 'game_initialized' not in st.session_state:
        st.session_state.game_initialized = True
        st.session_state.screen = 'start_game'
        st.session_state.metrics = INITIAL_METRICS.copy()
        st.session_state.budget = INITIAL_BUDGET
        st.session_state.human_resources = INITIAL_HR
        st.session_state.crisis_history = []
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_sequence = []
        st.session_state.selected_scenario_id = None
        st.session_state.decision = {}
        st.session_state.results = None

def reset_game():
    """Resets the game to its initial state."""
    st.session_state.game_initialized = False
    initialize_game_state()
    st.rerun()

def calculate_effects(action: ActionCard, scope: str, duration: str, safeguards: List[str]) -> Dict:
    """Calculates the effects of a player's decision on the game metrics."""
    # --- Constants for calculation clarity ---
    THREAT_SEVERITY = 80
    RANDOM_FACTOR_RANGE = (0.1, 0.3)
    SCOPE_MULTIPLIERS = {'targeted': 0.7, 'general': 1.3}
    DURATION_MULTIPLIERS = {'short': 0.5, 'medium': 1.0, 'long': 1.5}
    SAFEGUARD_QUALITY_PER_ITEM = 0.2
    TRUST_BOOST_FOR_TRANSPARENCY = 10
    FATIGUE_PER_DURATION = {'targeted': 5, 'general': 10}

    # --- Calculation logic ---
    random_factor = random.uniform(*RANDOM_FACTOR_RANGE)
    scope_multiplier = SCOPE_MULTIPLIERS[scope]
    duration_multiplier = DURATION_MULTIPLIERS[duration]
    safeguard_quality = len(safeguards) * SAFEGUARD_QUALITY_PER_ITEM

    security_change = (THREAT_SEVERITY * action.security_effect / 100) - (action.side_effect_risk * random_factor * 20)
    freedom_cost = action.freedom_cost * scope_multiplier * duration_multiplier * (1 - safeguard_quality * action.safeguard_reduction)
    public_trust_change = (TRUST_BOOST_FOR_TRANSPARENCY if 'transparency' in safeguards else 0) - (freedom_cost * 0.5)
    resilience_change = (action.security_effect * safeguard_quality / 2) if action.speed == 'slow' else 5
    fatigue_change = duration_multiplier * FATIGUE_PER_DURATION[scope]

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

# --- UI COMPONENTS ---
# Reusable functions for rendering parts of the UI.

def display_metrics_sidebar():
    """Displays the main status dashboard in the sidebar."""
    st.sidebar.header("📊 Durum Panosu")
    metrics_data = [
        ('Bütçe', st.session_state.budget, INITIAL_BUDGET),
        ('İnsan Kaynağı', st.session_state.human_resources, INITIAL_HR),
        ('Güvenlik', st.session_state.metrics['security'], 100),
        ('Özgürlük', st.session_state.metrics['freedom'], 100),
        ('Kamu Güveni', st.session_state.metrics['public_trust'], 100),
        ('Dayanıklılık', st.session_state.metrics['resilience'], 100),
        ('Uyum Yorgunluğu', st.session_state.metrics['fatigue'], 100)
    ]
    for name, value, max_value in metrics_data:
        st.sidebar.markdown(f"**{name}**")
        st.sidebar.progress(min(max(value / max_value, 0), 1))
        st.sidebar.markdown(f"<div style='text-align: right;'>{value:.1f} / {max_value}</div>", unsafe_allow_html=True)

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
    <div class="crisis-card" style="background-color: #e8f0fe; border-left: 5px solid #1f77b4;">
        💡 <strong>Rehber</strong>: {text}
    </div>
    """, unsafe_allow_html=True)


# --- SCREEN RENDERERS ---
# Functions responsible for drawing each screen of the game.

def start_game_screen():
    st.title("🛡️ CIO Kriz Yönetimi Oyunu")
    st.markdown("""
        <div class="crisis-card">
            <h2>Hoş Geldiniz!</h2>
            <p>Bu oyunda, bir CIO (Chief Information Officer) olarak, ada ülkenizi vuran bir dizi krizle yüzleşeceksiniz. Kararlarınız halkın güvenliğini, özgürlüklerini ve gelecekteki krizlere karşı dayanıklılığını şekillendirecek.</p>
            <p>Üç krizlik bir mücadele sizi bekliyor. Her kriz, bir önceki kararlarınızın sonuçlarını miras alacak. Hazır mısınız?</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Oyunu Başlat"):
        scenarios = get_scenarios()
        crisis_keys = list(scenarios.keys())
        random.shuffle(crisis_keys)
        st.session_state.crisis_sequence = crisis_keys[:MAX_CRISES]
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_history.append(st.session_state.metrics.copy())
        st.session_state.selected_scenario_id = st.session_state.crisis_sequence[0]
        st.session_state.screen = 'story'
        st.rerun()

def story_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title(f"{scenario.icon} Kriz {st.session_state.current_crisis_index + 1}: {scenario.title}")

    # Split the story into 'report' and 'mission' for a better layout
    try:
        report_part, mission_part = scenario.story.split("**Görev**:")
    except ValueError:
        # Fallback if the delimiter is not found
        report_part = scenario.story
        mission_part = ""

    # Display cards vertically to prevent overflow
    st.markdown(f"""
        <div class="crisis-card">
            {report_part}
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="crisis-card" style="border-left: 5px solid #ff7f0e;">
            <h4>Görev</h4>
            <hr>
            <p>{mission_part}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer

    display_guidance("Kararlarınız can güvenliğini artırabilir, ancak özgürlükleri ve halkın güvenini etkileyebilir. Dengeyi bulmaya hazır mısınız?")
    
    if st.button("Danışmanları Dinle"):
        st.session_state.screen = 'advisors'
        st.rerun()

def advisors_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title("Danışman Görüşleri")
    
    # Use columns to display advisor cards side-by-side
    cols = st.columns(len(scenario.advisors))
    for i, advisor in enumerate(scenario.advisors):
        with cols[i]:
            st.markdown(f"""
            <div class="crisis-card">
                <h5>{advisor.name}</h5>
                <hr>
                <p>{advisor.text}</p>
            </div>
            """, unsafe_allow_html=True)

    display_guidance("Her danışmanın önerisi farklı bir strateji sunuyor. Önyargılarına dikkat edin ve uzun vadeli etkileri düşünün!")

    if st.button("Karar Aşamasına Geç"):
        st.session_state.screen = 'decision'
        st.rerun()

def decision_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    st.title("Karar Paneli")

    # Display resources
    st.markdown(f"""
        <div class="crisis-card">
            <h3>Kaynaklar</h3>
            <p><strong>Mevcut Bütçe</strong>: {st.session_state.budget} | <strong>İnsan Kaynağı</strong>: {st.session_state.human_resources}</p>
        </div>
    """, unsafe_allow_html=True)

    # Action selection using cards
    st.subheader("Aksiyon Seç")
    cols = st.columns(len(scenario.action_cards))
    selected_action_id = st.session_state.decision.get('action')

    for i, card in enumerate(scenario.action_cards):
        with cols[i]:
            is_selected = selected_action_id == card.id
            border_style = "border: 2px solid #ff7f0e;" if is_selected else "border: 1px solid #e6e6e6;"
            st.markdown(f"""
                <div class="crisis-card" style="{border_style}">
                    <h5>{card.name}</h5>
                    <p>{card.tooltip}</p>
                    <small>Maliyet: {card.cost} 💰 | HR: {card.hr_cost} 👥 | Hız: {card.speed.capitalize()}</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Bunu Seç", key=f"select_{card.id}"):
                st.session_state.decision['action'] = card.id
                st.rerun()
    
    if selected_action_id:
        # Policy adjustments
        st.subheader("Politika Ayarları")
        with st.container():
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
            
            # Check for resources
            if st.session_state.budget < action.cost or st.session_state.human_resources < action.hr_cost:
                st.error(f"Bütçe ({st.session_state.budget}/{action.cost}) veya insan kaynağı ({st.session_state.human_resources}/{action.hr_cost}) yetersiz! Daha düşük maliyetli bir aksiyon seçin.")
            else:
                st.session_state.decision.update({
                    'scope': 'targeted' if scope == "Hedefli" else 'general',
                    'duration': {'Kısa': 'short', 'Orta': 'medium', 'Uzun': 'long'}[duration],
                    'safeguards': safeguards
                })
                results = calculate_effects(action, st.session_state.decision['scope'], st.session_state.decision['duration'], safeguards)
                st.session_state.results = results
                st.session_state.budget = results['budget']
                st.session_state.human_resources = results['human_resources']
                st.session_state.screen = 'immediate'
                st.rerun()

def immediate_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    action_name = next(card.name for card in scenario.action_cards if card.id == st.session_state.decision['action'])
    results = st.session_state.results
    old_metrics = st.session_state.metrics

    st.title("Anında Etki")
    st.markdown(f"""
        <div class="crisis-card">
            <h3>Olay Günlüğü</h3>
            <p>{scenario.immediate_text.format(f"<b>{action_name}</b>")}</p>
            <h4>Durum Güncellemesi</h4>
            <ul>
                <li><strong>Güvenlik</strong>: <span class="{'metric-positive' if results['security'] > old_metrics['security'] else 'metric-negative'}">{results['security']:.1f}</span> – Krizin acil etkileri hafifledi.</li>
                <li><strong>Özgürlük</strong>: <span class="{'metric-positive' if results['freedom'] > old_metrics['freedom'] else 'metric-negative'}">{results['freedom']:.1f}</span> – Kapsam ve süre özgürlükleri etkiledi.</li>
                <li><strong>Kamu Güveni</strong>: <span class="{'metric-positive' if results['public_trust'] > old_metrics['public_trust'] else 'metric-negative'}">{results['public_trust']:.1f}</span> – Şeffaflık tepkileri şekillendirdi.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Bir Süre Sonra..."):
        st.session_state.screen = 'delayed'
        st.rerun()

def delayed_screen():
    scenario = get_scenarios()[st.session_state.selected_scenario_id]
    
    # Apply delayed effects
    current_results = st.session_state.results
    delayed_results = {
        **current_results,
        'security': min(100, current_results['security'] + (10 if st.session_state.decision['action'] == 'C' else 5)),
        'resilience': min(100, current_results['resilience'] + (10 if st.session_state.decision['action'] == 'C' else 5)),
        'public_trust': min(100, max(0, current_results['public_trust'] - (3 if random.random() > 0.7 else 0)))
    }
    st.session_state.results = delayed_results

    st.title("Gecikmeli Etkiler")
    st.markdown(f"""
        <div class="crisis-card">
            <h3>Olay Günlüğü</h3>
            <p>{scenario.delayed_text}</p>
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
    # Update metrics and history for the current round
    st.session_state.metrics = st.session_state.results.copy()
    if len(st.session_state.crisis_history) <= st.session_state.current_crisis_index:
        st.session_state.crisis_history.append(st.session_state.metrics)

    st.title(f"Kriz {st.session_state.current_crisis_index + 1} Sonu Raporu")
    
    # Results Chart
    st.markdown('<div class="crisis-card"><h3>Sonuçlar</h3>', unsafe_allow_html=True)
    
    # Get previous metrics from history
    previous_metrics = st.session_state.crisis_history[st.session_state.current_crisis_index]
    current_metrics = st.session_state.metrics

    df = pd.DataFrame([
        {'Gösterge': 'Güvenlik', 'Başlangıç': previous_metrics['security'], 'Son': current_metrics['security']},
        {'Gösterge': 'Özgürlük', 'Başlangıç': previous_metrics['freedom'], 'Son': current_metrics['freedom']},
        {'Gösterge': 'Kamu Güveni', 'Başlangıç': previous_metrics['public_trust'], 'Son': current_metrics['public_trust']},
        {'Gösterge': 'Dayanıklılık', 'Başlangıç': previous_metrics['resilience'], 'Son': current_metrics['resilience']},
        {'Gösterge': 'Uyum Yorgunluğu', 'Başlangıç': previous_metrics['fatigue'], 'Son': current_metrics['fatigue']}
    ])
    
    # Prepare data for the grouped bar chart
    report_df_melted = df.melt(id_vars=['Gösterge'], value_vars=['Başlangıç', 'Son'], var_name='Durum', value_name='Değer')
    
    bar_chart = alt.Chart(report_df_melted).mark_bar().encode(
        x=alt.X('Durum:N', title=None, axis=alt.Axis(labels=True, ticks=False, domain=False)),
        y=alt.Y('Değer:Q', title='Puan', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Durum:N', title='Durum', scale=alt.Scale(domain=['Başlangıç', 'Son'], range=['#1f77b4', '#ff7f0e'])),
        column=alt.Column('Gösterge:N', title='Metrikler', header=alt.Header(labelOrient='bottom', titleOrient='bottom'))
    ).properties(
        width=alt.Step(40), # Controls the width of the bars
        title='Metriklerin Başlangıç ve Son Değerleri'
    ).configure_title(
        fontSize=16,
        anchor='middle'
    ).configure_view(
        stroke=None
    )
    
    st.altair_chart(bar_chart, use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)


    # Counter-factual analysis
    st.markdown(f"""
        <div class="crisis-card">
            <h3>Karşı-Olgu Analizi</h3>
            <p><i>{st.session_state.results['counter_factual']}</i></p>
            <p><strong>Analiz:</strong> Geniş kapsam veya uzun süre, ifade ve mahremiyeti etkiledi. Seçtiğiniz <strong>{len(st.session_state.decision['safeguards'])} güvence</strong>, özgürlük kaybını yaklaşık %{len(st.session_state.decision['safeguards']) * 15} oranında azalttı.</p>
        </div>
    """, unsafe_allow_html=True)

    # Real-world connection
    st.markdown("""
        <div class="crisis-card">
            <h3>Gerçek Dünya Bağlantısı</h3>
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
        if st.session_state.current_crisis_index < len(st.session_state.crisis_sequence):
            st.session_state.selected_scenario_id = st.session_state.crisis_sequence[st.session_state.current_crisis_index]
            # Reset decision for the new round
            st.session_state.decision = {}
            st.session_state.screen = 'story'
        else:
            st.session_state.screen = 'game_end'
        st.rerun()

def game_end_screen():
    st.title("🏆 Oyun Sonu: Krizler Tarihi")
    st.balloons()
    
    # Final score and Leadership Style
    final_metrics = st.session_state.results
    leadership_score = (final_metrics['security'] + final_metrics['freedom'] + final_metrics['public_trust']) / 3
    
    score_text = ""
    if leadership_score > 75:
        score_text = 'Mükemmel! Güvenlik, özgürlük ve kamu güvenini dengede tuttunuz.'
    elif leadership_score > 55:
        score_text = 'İyi iş, ama bazı alanlarda daha az maliyetli yollar mümkündü.'
    else:
        score_text = 'Zorlu bir yolculuktu. Daha fazla güvence ve hedefli önlem deneyin.'

    # Leadership Style Logic
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
            <p><i>{score_text}</i></p>
            <hr>
            <h4>Liderlik Tarzınız: {leadership_style}</h4>
            <p>{style_description}</p>
        </div>
    """, unsafe_allow_html=True)

    # Line chart of metric history
    history_df = pd.DataFrame(st.session_state.crisis_history)
    history_df['Kriz'] = [f"Kriz {i}" for i in range(len(history_df))]
    history_df.loc[0, 'Kriz'] = "Başlangıç"
    
    history_df = history_df.melt(id_vars=['Kriz'], var_name='Gösterge', value_name='Değer')
    metric_map = {'security': 'Güvenlik', 'freedom': 'Özgürlük', 'public_trust': 'Kamu Güveni', 'resilience': 'Dayanıklılık', 'fatigue': 'Uyum Yorgunluğu'}
    history_df = history_df[history_df['Gösterge'].isin(metric_map.keys())]
    history_df['Gösterge'] = history_df['Gösterge'].replace(metric_map)
    
    line_chart = alt.Chart(history_df).mark_line(point=True).encode(
        x=alt.X('Kriz:O', sort=None, title='Aşama'),
        y=alt.Y('Değer:Q', title='Puan', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Gösterge:N', title='Metrikler'),
        tooltip=['Kriz', 'Gösterge', alt.Tooltip('Değer:Q', format='.1f')]
    ).properties(
        title='Krizler Boyunca Metrik Değişimleri',
        height=400
    ).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

    if st.button("Yeni Oyun Başlat"):
        reset_game()

# --- MAIN APPLICATION FLOW ---
# The router that directs to the correct screen function.
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

# Get the function for the current screen and call it
current_screen_func = screen_functions.get(st.session_state.screen)
if current_screen_func:
    current_screen_func()
    display_help_guide()
else:
    st.error("Bir hata oluştu. Oyun yeniden başlatılıyor.")
    reset_game()
 