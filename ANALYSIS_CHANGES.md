
# Dettaglio Modifiche al file `analysis.py`

Ecco una spiegazione riga per riga delle modifiche apportate per introdurre le nuove metriche.

## 1. Calcolo dell'Entropia (Nuovo Metodo)
Ho aggiunto il metodo statico `calculate_entropy` alla classe `SimulationRunner`.

> **Vedi Codice:** [analysis.py:133-162](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L133-L162)

```python
@staticmethod
def calculate_entropy(grid):
    """
    Calculates the Shannon Entropy of the spatial distribution of the grid.
    """
    # ... (calcolo dei vicini per ogni cella) ...
    # Applica il padding periodico per gestire correttamente le condizioni al contorno (toroidali)
    padded = np.pad(grid, pad_width=1, mode='wrap')
    
    # Conta i vicini sommando le 8 direzioni
    # Questo ci dà una misura della "complessità" locale
    neighbors = np.zeros_like(grid, dtype=int)
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0: continue
            neighbors += padded[1+i:1+i+grid.shape[0], 1+j:1+j+grid.shape[1]]
    
    # Istogramma: Quante celle hanno 0 vicini? Quante 1? ... Quante 8?
    counts = np.bincount(neighbors.flatten(), minlength=9)
    
    # Normalizzazione per ottenere probabilità (p)
    probs = counts / np.sum(counts)
    probs = probs[probs > 0] # Rimuoviamo gli zeri per evitare log(0)
    
    # Formula di Shannon: -Sum(p * log2(p))
    entropy = -np.sum(probs * np.log2(probs))
    return entropy
```

## 2. Aggiornamento del Loop di Simulazione (`run`)
Ho modificato il metodo `run` per inizializzare le nuove liste dati e calcolare le metriche ad ogni step.

> **Inizializzazione Dizionario:** [analysis.py:189-199](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L189-L199)
```python
results = {
    # ...
    "entropy": [],      # Lista per salvare l'entropia a ogni step
    "activity": [],     # Lista per salvare il flusso (celle cambiate)
    "heatmap": np.zeros((rows, cols), dtype=int), # Griglia accumulatore per la heatmap
    # ...
}
```

> **Raccolta Dati nel Loop:** [analysis.py:215-228](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L215-L228)
```python
# 3. Entropy
ent = SimulationRunner.calculate_entropy(state)
results["entropy"].append(ent)

# 4. Activity (Flux)
if prev_state is None:
    flux = 0 
else:
    # XOR logico: True solo se lo stato è cambiato (Alive->Dead o Dead->Alive)
    flux = np.sum(np.logical_xor(state, prev_state))
results["activity"].append(flux)
prev_state = state

# 5. Heatmap Accumulation
# Somma 1 alla griglia heatmap se la cella è viva
results["heatmap"] += state.astype(int)
```

## 3. Generazione del Report (`generate_report`)
Ho ridisegnato il layout del grafico (da 2x2 a 2x3 o simile) per includere i nuovi plot.

> **Nuovo Layout:** [analysis.py:266](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L266)
```python
# GridSpec: 2 righe, 3 colonne. 
# La terza colonna (stats) è più stretta (width_ratios=[1, 1, 0.4])
gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.4])
```

> **Plot 3: Entropia & Attività (Doppio Asse):** [analysis.py:295-309](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L295-L309)
```python
# Asse Sinistro (Viola): Entropia
ax_ent.plot(data["entropy"], color='tab:purple', ...)

# Asse Destro (Arancione): Attività
ax_act = ax_ent.twinx() # Crea un secondo asse Y che condivide lo stesso asse X
ax_act.plot(data["activity"], color='tab:orange', ...)
```

> **Plot 4: Heatmap:** [analysis.py:312-318](file:///c%3A/Users/Nicola%20Lavarda/Jupyter/LCP_projects_Y8_Group1/LCP_projects_Y8_Group1/analysis.py#L312-L318)
```python
# Visualizza la matrice accumulata "heatmap" usando una mappa di calore 'hot'
im = ax_heat.imshow(data["heatmap"], cmap='hot', interpolation='nearest')
```
