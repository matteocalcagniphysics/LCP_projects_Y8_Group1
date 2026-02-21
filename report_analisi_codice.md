# Report Tecnico: `analysis.py` — Logica del Codice e Calcoli

**File:** `analysis.py`  
**Progetto:** Conway's Game of Life — Suite di Analisi  
**Data:** 2026-02-21  

---

## Indice

1. [Struttura generale del codice](#1-struttura-generale-del-codice)
2. [Configurazione degli esperimenti (TEST_SUITE)](#2-configurazione-degli-esperimenti-test_suite)
3. [Classe `SimulationRunner`: il motore analitico](#3-classe-simulationrunner-il-motore-analitico)
   - [3.1 Centro di massa (`get_center_of_mass`)](#31-centro-di-massa-get_center_of_mass)
   - [3.2 Rilevamento del periodo (`detect_period`)](#32-rilevamento-del-periodo-detect_period)
   - [3.3 Classificazione del comportamento (`classify_behavior`)](#33-classificazione-del-comportamento-classify_behavior)
   - [3.4 Calcolo dell'Entropia di Shannon (`calculate_entropy`)](#34-calcolo-dellentropia-di-shannon-calculate_entropy)
   - [3.5 Ciclo principale di simulazione (`run`)](#35-ciclo-principale-di-simulazione-run)
4. [Calcolo dell'Attività / Flux](#4-calcolo-dellattivit--flux)
5. [Motore di reporting (`generate_report`)](#5-motore-di-reporting-generate_report)
6. [Diagramma del flusso di esecuzione](#6-diagramma-del-flusso-di-esecuzione)

---

## 1. Struttura generale del codice

Il file `analysis.py` è organizzato in quattro sezioni principali:

| Sezione | Righe | Descrizione |
|---|---|---|
| **1. Configurazione** | 14–65 | Lista degli esperimenti da eseguire (`TEST_SUITE`) |
| **2. Core Analytics** | 71–247 | Classe `SimulationRunner` con tutti i calcoli fisici |
| **3. Reporting** | 253–359 | Funzione `generate_report` che produce i grafici PNG |
| **4. Main Execution** | 366–387 | Loop principale che itera su tutti gli esperimenti |

Le dipendenze esterne usate sono:
- `numpy` — calcolo matriciale e vettoriale sui griglie
- `matplotlib` — generazione dei grafici

---

## 2. Configurazione degli esperimenti (`TEST_SUITE`)

`TEST_SUITE` è una lista di dizionari Python. Ogni dizionario descrive un esperimento:

```python
{
    "name": "Glider_Trajectory",   # Identificativo univoco (usato per il nome del file output)
    "category": "Spaceship",       # Categoria del pattern (usata da insert_pattern)
    "pattern_name": "Glider",      # Nome del pattern specifico
    "pos": (5, 5),                 # Posizione (riga, colonna) di inserimento nella griglia
    "steps": 100,                  # Numero di generazioni da simulare
    "grid_size": (60, 60)          # Dimensioni della griglia (righe x colonne)
}
```

I sei esperimenti configurati coprono le categorie fondamentali del Game of Life:

| Nome | Categoria | Comportamento atteso |
|---|---|---|
| `Block_Stability` | Still Life | Struttura immobile, nessun cambiamento |
| `Blinker_Oscillation` | Oscillator | Oscillazione con periodo 2 |
| `Pulsar_Oscillation` | Oscillator | Oscillazione complessa, periodo 3 |
| `Glider_Trajectory` | Spaceship | Moto traslatorio diagonale |
| `Gosper_Gun_Growth` | Complex | Crescita illimitata tramite emissione di glider |
| `Random_Entropy` | Random | Evoluzione caotica da stato casuale |

---

## 3. Classe `SimulationRunner`: il motore analitico

La classe `SimulationRunner` contiene esclusivamente metodi statici (`@staticmethod`), ovvero funzioni pure che non dipendono da stato interno dell'istanza. Questo le rende indipendenti e facilmente testabili.

### 3.1 Centro di massa (`get_center_of_mass`)

```python
@staticmethod
def get_center_of_mass(grid):
    indices = np.argwhere(grid)         # Trova gli indici (riga, col) delle celle vive
    if indices.size == 0:
        return np.nan, np.nan           # Griglia vuota: nessun centro definito
    mean_pos = np.mean(indices, axis=0) # Media posizione di tutte le celle vive
    return mean_pos[0], mean_pos[1]     # Restituisce (riga_media, colonna_media)
```

**Logica:**  
`np.argwhere(grid)` restituisce un array di shape `(N, 2)` dove N è il numero di celle vive e ogni riga contiene `[row, col]` di una cella viva. La media lungo `axis=0` calcola la posizione media (centroide) di tutte le celle vive.

**Formula matematica:**

$$\text{CoM} = \left(\frac{\sum_{i} r_i}{N},\ \frac{\sum_{i} c_i}{N}\right)$$

dove $r_i$ e $c_i$ sono riga e colonna dell'$i$-esima cella viva e $N$ è la popolazione totale.

---

### 3.2 Rilevamento del periodo (`detect_period`)

```python
@staticmethod
def detect_period(timeline):
    last_state = timeline[-1]            # Ultimo frame della simulazione
    n_steps = len(timeline)
    search_limit = min(n_steps, 200)     # Limite di ricerca: max 200 passi indietro

    for i in range(n_steps - 2, n_steps - 2 - search_limit, -1):
        if i < 0: break
        if np.array_equal(last_state, timeline[i]):
            return (n_steps - 1) - i     # Distanza = periodo
    return -1                            # Nessun periodo trovato → sistema caotico
```

**Logica:**  
Partendo dall'ultimo stato della simulazione, si scorrono all'indietro tutti gli stati precedenti. Il primo stato uguale all'ultimo trovato determina il **periodo**: la distanza temporale tra i due stati identici.

| Valore restituito | Significato |
|---|---|
| `1` | Struttura stabile (Still Life) |
| `2, 3, ...` | Oscillatore (periodo N) o Spaceship |
| `-1` | Nessuna periodicità rilevata (caotico/in transizione) |

---

### 3.3 Classificazione del comportamento (`classify_behavior`)

```python
@staticmethod
def classify_behavior(period, displacement, population_trend):
    start_pop, end_pop = population_trend

    if end_pop == 0:                          return "Extinction"
    if period == 1:                           return "Still Life (Stable)"
    if period > 1:
        if displacement > 2.0:               return f"Spaceship / Mover (Period {period})"
        else:                                return f"Oscillator (Period {period})"
    if end_pop > start_pop * 1.5:            return "Unbounded Growth / Gun"
    return "Chaotic / Complex Stabilization"
```

**Logica delle euristiche:**

1. **Extinction:** la popolazione finale è zero → tutte le celle sono morte.
2. **Still Life:** periodo = 1 → l'ultimo stato è identico a quello immediatamente precedente.
3. **Spaceship vs Oscillator:** se c'è periodo E lo spostamento del centro di massa è > 2.0 celle, il pattern si è mosso nello spazio → è uno Spaceship. Altrimenti oscilla sul posto.
4. **Unbounded Growth:** senza periodo rilevato ma con crescita > 150% della popolazione iniziale → probabilmente è un cannone (Gun).
5. **Chaotic:** tutto il resto → comportamento complesso non classificabile.

---

### 3.4 Calcolo dell'Entropia di Shannon (`calculate_entropy`)

Questa è la metrica più sofisticata del codice. Misura la **complessità della distribuzione spaziale** della griglia tramite l'entropia di Shannon applicata alla distribuzione del conteggio dei vicini.

#### Step 1 — Padding con bordi periodici

```python
padded = np.pad(grid, pad_width=1, mode='wrap')
```

La griglia viene espansa di 1 cella su tutti i lati usando la modalità `wrap` (bordi toroidali). Questo significa che la cella in posizione `(0,0)` è considerata vicina alla cella in `(-1, -1)` come se la griglia si chiudesse su sé stessa, evitando effetti di bordo artificiali.

**Esempio visivo** (griglia 3×3):
```
Originale:    Padded (5×5 con wrap):
1 0 1         1 0 1 0 1
0 1 0    →    1 0 1 0 1
1 0 1         0 1 0 1 0
              1 0 1 0 1
              0 1 0 1 0
```

#### Step 2 — Calcolo dei vicini per ogni cella

```python
neighbors = np.zeros_like(grid, dtype=int)
for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
        if i == 0 and j == 0: continue   # Esclude la cella stessa
        neighbors += padded[1+i:1+i+grid.shape[0], 1+j:1+j+grid.shape[1]]
```

Il doppio loop itera sui **8 offset** dei vicini `(i, j)` ∈ {-1, 0, 1}² escluso `(0,0)`. Per ogni offset, si estrae uno "shift" della griglia padded e si somma al contatore. Il risultato è un array `neighbors` dove ogni cella contiene quanti dei suoi 8 vicini sono vivi (valore da 0 a 8).

**Perché questo approccio?** Invece di usare un loop Python su ogni cella (lento), questa implementazione vettorizzata con NumPy opera su intere matrici contemporaneamente (veloce).

#### Step 3 — Istogramma delle frequenze vicini

```python
counts = np.bincount(neighbors.flatten(), minlength=9)
```

`np.bincount` conta quante celle hanno 0 vicini, quante ne hanno 1, ..., quante ne hanno 8. Il risultato è un array di 9 elementi: `counts[k]` = numero di celle con esattamente k vicini vivi.

**Esempio:** su una griglia 50×50 (2500 celle totali):
```
counts = [1800, 400, 150, 70, 40, 20, 12, 5, 3]
         ↑ 1800 celle con 0 vicini
                ↑ 400 celle con 1 vicino
                      ...
```

#### Step 4 — Distribuzione di probabilità

```python
total = np.sum(counts)
probs = counts / total          # Normalizza: probs[k] = P(k vicini)
probs = probs[probs > 0]        # Rimuovi probabilità zero (evita log(0))
```

Si ottiene la distribuzione di probabilità $P(k)$ per $k = 0, \ldots, 8$, cioè la probabilità che una cella scelta a caso abbia esattamente $k$ vicini vivi.

#### Step 5 — Formula dell'Entropia di Shannon

```python
entropy = -np.sum(probs * np.log2(probs))
```

**Formula matematica:**

$$H = -\sum_{k=0}^{8} P(k) \cdot \log_2 P(k)$$

**Interpretazione fisica:**

| Valore di H | Significato |
|---|---|
| **H ≈ 0** | Distribuzione concentrata: tutte le celle hanno lo stesso numero di vicini (pattern molto ordinato, es. griglia vuota: tutte 0 vicini) |
| **H massima ≈ 3.17** | Distribuzione uniforme su tutti i 9 valori possibili: massima disomogeneità spaziale |
| **H intermedia** | Pattern parzialmente strutturati con varianza nella densità locale |

**Esempio numerico:**
- **Griglia vuota:** tutte le celle hanno 0 vicini → P(0) = 1, P(k>0) = 0 → H = 0
- **Glider in movimento:** distribuzione varia a ogni passo → H moderata e variabile nel tempo
- **Gosper Gun attivo:** molte glider, alta varietà di configurazioni locali → H elevata
- **Stato casuale iniziale:** la distribuzione di vicini segue una binomiale → H ≈ massima

---

## 4. Calcolo dell'Attività / Flux

L'**attività** (chiamata anche *flux* nel codice) è la segunda metrica dinamica calcolata nel loop di evoluzione.

```python
# Nel ciclo di evoluzione (metodo run):
prev_state = None

for state in timeline:
    # ...
    if prev_state is None:
        flux = 0                                           # Primo frame: nessun confronto possibile
    else:
        flux = np.sum(np.logical_xor(state, prev_state))  # XOR logico tra frame consecutivi
    results["activity"].append(flux)
    prev_state = state
```

#### Logica dell'operazione XOR

`np.logical_xor(state, prev_state)` confronta due griglie booleane cella per cella:

| `prev_state[i,j]` | `state[i,j]` | `XOR` | Significato |
|---|---|---|---|
| `False` (morta) | `False` (morta) | `False` | Cella rimasta morta |
| `True` (viva) | `True` (viva) | `False` | Cella rimasta viva |
| `False` (morta) | `True` (viva) | **`True`** | **Cella nata** (nascita) |
| `True` (viva) | `False` (morta) | **`True`** | **Cella morta** (morte) |

`np.sum(...)` conta quindi il numero totale di celle che hanno **cambiato stato** tra una generazione e la successiva. Questo include sia le nascite che le morti.

**Formula matematica:**

$$\text{Activity}(t) = \sum_{i,j} \left[ \text{state}(t)_{i,j} \oplus \text{state}(t-1)_{i,j} \right]$$

dove $\oplus$ è l'operatore XOR.

**Interpretazione fisica:**

| Valore dell'Attività | Significato |
|---|---|
| **0** | Sistema completamente stabile (Still Life) |
| **Costante e bassa** | Oscillatore: le stesse celle cambiano ogni periodo |
| **Costante e alta** | Spaceship o Gun: continua generazione di nuove strutture |
| **Decrescente** | Il sistema si sta stabilizzando (transiente) |
| **Irregolare/caotica** | Sistema complesso non periodico |

**Relazione con l'Entropia:**  
Entropia e Attività misurano aspetti complementari:
- L'**Entropia** misura la complessità della *struttura spaziale* istantanea.
- L'**Attività** misura la *dinamica temporale*, ovvero quanto velocemente la struttura cambia.

Un pattern con alta entropia ma bassa attività è spazialmente complesso ma temporalmente stabile. Un pattern con bassa entropia e alta attività cambia rapidamente ma in modo semplice e regolare.

---

## 5. Motore di reporting (`generate_report`)

La funzione `generate_report` produce un report visivo in formato PNG con 5 pannelli:

```
┌─────────────────────┬────────────────────────┬─────────────┐
│  1. Population      │  3. Entropy & Activity │             │
│     Evolution       │     (doppio asse Y)    │  5. Data    │
│     (linea blu)     │     (viola + arancio)  │     Card    │
├─────────────────────┼────────────────────────┤  (testo)    │
│  2. Center of Mass  │  4. Occupancy         │             │
│     Trajectory      │     Heatmap            │             │
│     (linea rossa)   │     (cmap 'hot')       │             │
└─────────────────────┴────────────────────────┴─────────────┘
```

#### Pannello 3: Entropia & Attività con doppio asse Y

```python
ax_ent = fig.add_subplot(gs[0, 1])

# Asse Y sinistro: Entropia (viola, linea tratteggiata)
ax_ent.set_ylabel('Shannon Entropy', color='tab:purple')
ax_ent.plot(data["entropy"], color='tab:purple', linewidth=2, linestyle='--')

# Asse Y destro: Attività (arancione, linea continua)
ax_act = ax_ent.twinx()
ax_act.set_ylabel('Activity (Flux)', color='tab:orange')
ax_act.plot(data["activity"], color='tab:orange', linewidth=2, alpha=0.7)
```

Il metodo `ax_ent.twinx()` crea un secondo asse Y condividendo lo stesso asse X. Questo è necessario perché entropia (valori tipicamente 0–3) e attività (valori che possono essere dell'ordine di centinaia) hanno scale molto diverse.

#### Pannello 4: Heatmap di occupanza

```python
results["heatmap"] += state.astype(int)  # Accumulata nel loop
```

Per ogni generazione, la griglia booleana viene convertita in interi (True→1, False→0) e sommata alla heatmap. Il risultato finale mostra per quante generazioni ogni cella è stata viva. Celle con valore alto (bianco/giallo su colormap `hot`) sono state vive per molte generazioni; celle con valore 0 (nero) non sono mai state attive.

#### Data Card: statistiche derivate

```python
peak_entropy = max(data["entropy"])         # Massima entropia osservata
avg_activity = np.mean(data["activity"])    # Attività media per passo
```

Queste due statistiche sintetizzano il comportamento globale dell'esperimento in valori scalari facilmente confrontabili tra esperimenti diversi.

---

## 6. Diagramma del flusso di esecuzione

```
main()
  │
  ├─ Per ogni config in TEST_SUITE:
  │     │
  │     ├─ SimulationRunner.run(config)
  │     │     │
  │     │     ├─ Crea griglia zeros (rows×cols)
  │     │     ├─ insert_pattern() → griglia con pattern inserito
  │     │     ├─ evolution() → timeline[0..steps] (lista di stati)
  │     │     │
  │     │     └─ Per ogni stato in timeline:
  │     │           ├─ population = sum(state)
  │     │           ├─ occupancy = population / (rows*cols)
  │     │           ├─ (com_y, com_x) = get_center_of_mass(state)
  │     │           ├─ entropy = calculate_entropy(state)
  │     │           │     ├─ pad(grid, wrap)
  │     │           │     ├─ Somma 8 slices shifted → neighbors
  │     │           │     ├─ bincount(neighbors) → counts[0..8]
  │     │           │     ├─ probs = counts / total
  │     │           │     └─ H = -sum(p * log2(p))
  │     │           ├─ activity = sum(XOR(state, prev_state))
  │     │           └─ heatmap += state
  │     │
  │     │     Post-processing:
  │     │           ├─ detect_period(timeline)
  │     │           ├─ displacement = sqrt(dx²+dy²) del centro di massa
  │     │           └─ classify_behavior(period, displacement, pop_trend)
  │     │
  │     └─ generate_report(results) → PNG salvato in Analysis/
  │
  └─ Fine
```

---

## Appendice: Perché l'Entropia di Shannon sul conteggio vicini?

La scelta di applicare Shannon Entropy alla **distribuzione del numero di vicini** (e non, ad esempio, alla distribuzione di celle vive/morte) è motivata dal fatto che:

1. **Cattura la struttura locale:** il numero di vicini di una cella riflette la densità e la forma del pattern locale intorno ad essa.
2. **Sensibile alla varianza spaziale:** un pattern con alta varianza nella densità locale (aree dense vicino ad aree vuote) produrrà una distribuzione più piatta e quindi entropia più alta.
3. **Invarianza alla traslazione:** l'entropia è uguale per un pattern e la sua versione traslata nella griglia, rendendola una misura della struttura intrinseca e non della sua posizione.
4. **Legame con la complessità computazionale:** nell'ambito dei sistemi complessi, l'entropia spaziale è un indicatore proxy della complessità del sistema e della sua distanza dall'equilibrio.

In alternativa, si potrebbe calcolare l'entropia direttamente sulla distribuzione 0/1 delle celle (viva/morta), ma questa produrrebbe un unico bit di informazione non sensibile alla struttura spaziale. La scelta dei vicini come variabile casuale è quindi significativamente più informativa.
