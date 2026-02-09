import numpy as np
import matplotlib.pyplot as plt
import os
import gameoflife.evolution as cg
import gameoflife.patterns as pt

# ==========================================
# 1. CONFIGURATION SUITE
# ==========================================
# Define here all the experiments you want to run.
# The system will iterate through this list and generate a report for each.
# ==========================================

TEST_SUITE = [
    {
        "name": "Block_Stability",
        "category": "Still Life",
        "pattern_name": "Block",
        "pos": (25, 25),
        "steps": 50,
        "grid_size": (50, 50)
    },
    {
        "name": "Blinker_Oscillation",
        "category": "Oscillator",
        "pattern_name": "Blinker",
        "pos": (25, 25),
        "steps": 50,
        "grid_size": (50, 50)
    },
    {
        "name": "Pulsar_Oscillation",
        "category": "Oscillator",
        "pattern_name": "Pulsar",
        "pos": (20, 20),
        "steps": 100,
        "grid_size": (60, 60)
    },
    {
        "name": "Glider_Trajectory",
        "category": "Spaceship",
        "pattern_name": "Glider",
        "pos": (5, 5),
        "steps": 100,
        "grid_size": (60, 60)
    },
    {
        "name": "Gosper_Gun_Growth",
        "category": "Complex",
        "pattern_name": "Glider Gun",
        "pos": (5, 5),
        "steps": 150,
        "grid_size": (60, 80)
    },
    {
        "name": "Random_Entropy",
        "category": "Random",
        "pattern_name": "Random",
        "pos": (0, 0),
        "steps": 200,
        "grid_size": (80, 80)
    }
]

OUTPUT_DIR = "Analysis"

# ==========================================
# 2. CORE ANALYTICS ENGINE
# ==========================================

class SimulationRunner:
    """
    Encapsulates the logic for running simulations and calculating physics metrics.
    """

    @staticmethod
    def get_center_of_mass(grid):
        """
        Calculates the spatial center of mass of alive cells.
        Returns (row, col). Returns (NaN, NaN) if grid is empty.
        """
        indices = np.argwhere(grid)
        if indices.size == 0:
            return np.nan, np.nan
        mean_pos = np.mean(indices, axis=0)
        return mean_pos[0], mean_pos[1]

    @staticmethod
    def detect_period(timeline):
        """
        Analyzes the timeline backwards to find repeating patterns.
        Returns period (int) or -1 if chaotic/transient.
        """
        last_state = timeline[-1]
        n_steps = len(timeline)
        
        # Look backwards from the second-to-last frame
        # We limit the search to avoid performance issues on very long simulations
        search_limit = min(n_steps, 200) 
        
        for i in range(n_steps - 2, n_steps - 2 - search_limit, -1):
            if i < 0: break
            if np.array_equal(last_state, timeline[i]):
                return (n_steps - 1) - i
        return -1

    @staticmethod
    def classify_behavior(period, displacement, population_trend):
        """
        Heuristic function to classify the pattern based on observed metrics.
        """
        start_pop, end_pop = population_trend
        
        if end_pop == 0:
            return "Extinction"
        
        if period == 1:
            return "Still Life (Stable)"
        
        if period > 1:
            if displacement > 2.0: # Threshold for movement
                return f"Spaceship / Mover (Period {period})"
            else:
                return f"Oscillator (Period {period})"
        
        # If no period detected
        if end_pop > start_pop * 1.5:
            return "Unbounded Growth / Gun"
        
        return "Chaotic / Complex Stabilization"

    @staticmethod
    def calculate_entropy(grid):
        """
        Calculates the Shannon Entropy of the spatial distribution of the grid.
        """
        # Calculate neighbor counts for all active cells
        padded = np.pad(grid, pad_width=1, mode='wrap')
        neighbors = np.zeros_like(grid, dtype=int)
        
        # Sum all 8 neighbors
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0: continue
                # Slice and add
                neighbors += padded[1+i:1+i+grid.shape[0], 1+j:1+j+grid.shape[1]]
        
        # Compute histogram of neighbor counts (0 to 8)
        counts = np.bincount(neighbors.flatten(), minlength=9)
        
        # Normalize to probability distribution
        total = np.sum(counts)
        if total == 0: return 0.0
        
        probs = counts / total
        
        # Filter zero probabilities to avoid log(0)
        probs = probs[probs > 0]
        
        # Shannon Entropy: -Sum(p * log2(p))
        entropy = -np.sum(probs * np.log2(probs))
        return entropy

    @staticmethod
    def run(config):
        """
        Executes a single experiment configuration.
        """
        name = config["name"]
        cat = config["category"]
        p_name = config["pattern_name"]
        rows, cols = config["grid_size"]
        steps = config["steps"]
        
        print(f"[{name}] Initializing grid ({rows}x{cols})...")

        # --- A. Setup Grid ---
        grid = np.zeros((rows, cols), dtype=bool)
        
        # Inject pattern using Tina's library
        r_start, c_start = config["pos"]
        grid = pt.insert_pattern(grid, cat, p_name, r_start, c_start)

        # --- B. Evolution Loop ---
        print(f"[{name}] Simulating {steps} generations...")
        timeline = cg.evolution(genzero=grid, timesteps=steps)

        # --- C. Data Collection ---
        results = {
            "config": config,
            "population": [],
            "occupancy": [],
            "com_x": [],
            "com_y": [],
            "entropy": [],
            "activity": [],
            "heatmap": np.zeros((rows, cols), dtype=int),
            "displacement": 0.0
        }
        
        total_pixels = rows * cols
        prev_state = None

        for state in timeline:
            # 1. Population Metrics
            pop = np.sum(state)
            results["population"].append(pop)
            results["occupancy"].append(pop / total_pixels)
            
            # 2. Spatial Metrics (Center of Mass)
            r, c = SimulationRunner.get_center_of_mass(state)
            results["com_y"].append(r) # Row index maps to Y
            results["com_x"].append(c) # Col index maps to X

            # 3. Entropy
            ent = SimulationRunner.calculate_entropy(state)
            results["entropy"].append(ent)
            
            # 4. Activity (Flux)
            if prev_state is None:
                flux = 0 
            else:
                flux = np.sum(np.logical_xor(state, prev_state))
            results["activity"].append(flux)
            prev_state = state
            
            # 5. Heatmap Accumulation
            results["heatmap"] += state.astype(int)

        # --- D. Post-Processing Analysis ---
        results["period"] = SimulationRunner.detect_period(timeline)
        
        # Calculate net displacement
        if not np.isnan(results["com_x"][0]) and not np.isnan(results["com_x"][-1]):
            dx = results["com_x"][-1] - results["com_x"][0]
            dy = results["com_y"][-1] - results["com_y"][0]
            results["displacement"] = np.sqrt(dx**2 + dy**2)
        
        # Determine behavior type
        pop_trend = (results["population"][0], results["population"][-1])
        results["behavior"] = SimulationRunner.classify_behavior(
            results["period"], 
            results["displacement"], 
            pop_trend
        )

        return results

# ==========================================
# 3. REPORTING ENGINE
# ==========================================

def generate_report(data, output_folder):
    """
    Creates a detailed visual report and saves it to the disk.
    Includes Population, Trajectory, Entropy, Activity, and Heatmaps.
    """
    name = data["config"]["name"]
    filename = os.path.join(output_folder, f"report_{name}.png")
    
    # Create a figure with a grid layout (2 rows, 3 columns)
    # Col 1: Pop, Trajectory
    # Col 2: Entropy/Activity, Heatmap
    # Col 3: Stats
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.4])

    # --- Plot 1: Population History (Top Left) ---
    ax_pop = fig.add_subplot(gs[0, 0])
    ax_pop.plot(data["population"], color='#2E86C1', linewidth=2, label='Alive Cells')
    ax_pop.set_title("Population Evolution", fontweight='bold')
    ax_pop.set_ylabel("Count")
    ax_pop.legend(loc='upper right')
    ax_pop.grid(True, alpha=0.3)

    # --- Plot 2: Trajectory Map (Bottom Left) ---
    ax_traj = fig.add_subplot(gs[1, 0])
    
    # Plot path
    ax_traj.plot(data["com_x"], data["com_y"], color='#E74C3C', alpha=0.5, label='Path')
    
    # Plot Start and End points
    if len(data["com_x"]) > 0:
        ax_traj.scatter(data["com_x"][0], data["com_y"][0], c='green', s=100, marker='^', label='Start')
        ax_traj.scatter(data["com_x"][-1], data["com_y"][-1], c='red', s=100, marker='s', label='End')
    
    ax_traj.set_title("Center of Mass Trajectory")
    ax_traj.set_xlabel("Grid Column")
    ax_traj.set_ylabel("Grid Row")
    ax_traj.invert_yaxis() # Important for matrix visualization
    ax_traj.legend()
    ax_traj.grid(True, alpha=0.3)

    # --- Plot 3: Entropy & Activity (Top Middle) ---
    ax_ent = fig.add_subplot(gs[0, 1])
    
    # Dual axis
    color_ent = 'tab:purple'
    ax_ent.set_xlabel('Step')
    ax_ent.set_ylabel('Shannon Entropy', color=color_ent)
    ax_ent.plot(data["entropy"], color=color_ent, linewidth=2, linestyle='--')
    ax_ent.tick_params(axis='y', labelcolor=color_ent)
    ax_ent.set_title("Entropy & Activity (Flux)")
    
    ax_act = ax_ent.twinx()
    color_act = 'tab:orange'
    ax_act.set_ylabel('Activity (Flux)', color=color_act)
    ax_act.plot(data["activity"], color=color_act, linewidth=2, alpha=0.7)
    ax_act.tick_params(axis='y', labelcolor=color_act)

    # --- Plot 4: Occupancy Heatmap (Bottom Middle) ---
    ax_heat = fig.add_subplot(gs[1, 1])
    
    # Use log scale if there's huge variance, but linear is usually fine for short runs
    # Adding 1 to avoid log(0) issues if using LogNorm, but let's stick to linear for now.
    im = ax_heat.imshow(data["heatmap"], cmap='hot', interpolation='nearest')
    ax_heat.set_title("Occupancy Heatmap")
    fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.04)

    # --- Panel 5: Technical Data Card (Right Column) ---
    ax_info = fig.add_subplot(gs[:, 2])
    ax_info.axis('off')
    
    # Calculate new stats
    peak_entropy = max(data["entropy"]) if data["entropy"] else 0
    avg_activity = np.mean(data["activity"]) if data["activity"] else 0
    
    # Construct the text block
    cfg = data["config"]
    text_content = (
        f"EXPERIMENT REPORT: {name}\n"
        f"{'='*30}\n\n"
        f"CONFIGURATION:\n"
        f"• Pattern: {cfg['pattern_name']}\n"
        f"• Category: {cfg['category']}\n"
        f"• Grid Size: {cfg['grid_size']}\n"
        f"• Steps: {cfg['steps']}\n\n"
        f"STATISTICS:\n"
        f"• Initial Pop: {data['population'][0]}\n"
        f"• Final Pop: {data['population'][-1]}\n"
        f"• Peak Occupancy: {max(data['occupancy'])*100:.2f}%\n"
        f"• Peak Entropy: {peak_entropy:.2f}\n"
        f"• Avg Activity: {avg_activity:.1f} cells/step\n\n"
        f"PHYSICS ANALYSIS:\n"
        f"• Period Detected: {data['period'] if data['period'] > 0 else 'None'}\n"
        f"• Net Displacement: {data['displacement']:.2f} px\n"
        f"• Classification: \n  {data['behavior']}"
    )
    
    # Add text box
    ax_info.text(0.05, 0.95, text_content, 
                 fontsize=11, family='monospace', verticalalignment='top',
                 bbox=dict(boxstyle="round,pad=1", facecolor="#F8F9F9", edgecolor="#B2BABB"))

    # Save and Close
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close(fig) # Close to free up memory
    print(f"Saved report: {filename}")


# ==========================================
# 4. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    
    # 1. Prepare Output Directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    
    print(f"Starting Analysis Suite with {len(TEST_SUITE)} experiments...")
    
    # 2. Loop through experiments
    for config in TEST_SUITE:
        try:
            # Run Simulation
            result_data = SimulationRunner.run(config)
            
            # Generate Report
            generate_report(result_data, OUTPUT_DIR)
            
        except Exception as e:
            print(f"ERROR processing {config['name']}: {e}")

    print("\nAll experiments completed. Check the 'Analysis' folder.")