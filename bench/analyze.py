import argparse
import glob
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

def compute_metrics(filepath):
    df = pd.read_csv(filepath)
    total = len(df)
    ok = df[df["STATUS"] == 200]
    n_ok = len(ok)
    
    #Durée réelle du run (en secondes)
    duration_s = df["T_START"].max() - df["T_START"].min() if total > 1 else 0.0
    throughput_req_s = n_ok / duration_s if duration_s > 0 else 0.0
    
    #Taux d'erreur HTTP en %
    error_rate_pct = ((total - n_ok) / total * 100.0) if total > 0 else 0.0
    
    #Médianes sur les requêtes réussies
    latency_med_ms = ok["LATENCY_MS"].median() if n_ok > 0 else float("nan")
    server_med_ms = ok["SERVER_MS"].median() if n_ok > 0 else float("nan")
    
    #Nombre d'instances uniques actives en ignorant les valeurs vides 
    unique_instances = ok["INSTANCE"].dropna().nunique()
    
    return {
        "total_requests": total,
        "success_requests": n_ok,
        "duration_s": round(duration_s, 2),
        "throughput_req_s": round(throughput_req_s, 2),
        "latency_med_ms": round(latency_med_ms, 2),
        "server_med_ms": round(server_med_ms, 2),
        "error_rate_pct": round(error_rate_pct, 2),
        "unique_instances": int(unique_instances),
    }

def build_fig1a():
    #Impact de U (100, 1000, 10000) et P (10, 100, 1000)
    rows = []
    for u in [100, 1000, 10000]:
        matches = glob.glob(f"raw/*_u{u}.csv")
        if matches:
            m = compute_metrics(matches[0])
            rows.append({"dimension": "U", "value": u, **m})
    for p in [10, 100, 1000]:
        matches = glob.glob(f"raw/*_p{p}.csv")
        if matches:
            m = compute_metrics(matches[0])
            rows.append({"dimension": "P", "value": p, **m})
            
    df_out = pd.DataFrame(rows)
    df_out.to_csv("figures/fig1a.csv", index=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, dim, label in zip(axes, ["U", "P"], ["Utilisateurs (U)", "Posts par utilisateur (P)"]):
        sub = df_out[df_out["dimension"] == dim].sort_values("value")
        ax.plot(sub["value"], sub["latency_med_ms"], marker="o", label="Latence client médiane (ms)")
        ax.plot(sub["value"], sub["server_med_ms"], marker="s", linestyle="--", label="Server-Timing médian (ms)")
        ax.set_xscale("log")
        ax.set_xlabel(label)
        ax.grid(True, which="both", ls=":")
        ax.legend()
    axes[0].set_ylabel("Temps médian (ms)")
    fig.suptitle("Fig 1a — Temps de réponse médian selon U et P (1 client)")
    plt.tight_layout()
    plt.savefig("figures/fig1a.png", dpi=150)
    plt.close()

def build_fig1b():
    #Impact de F (5 à 100 par pas de 5)
    rows = []
    for f in range(5, 105, 5):
        matches = glob.glob(f"raw/*_f{f:02d}.csv") or glob.glob(f"raw/*_f{f}.csv")
        if matches:
            m = compute_metrics(matches[0])
            rows.append({"followees_F": f, **m})
            
    df_out = pd.DataFrame(rows).sort_values("followees_F")
    df_out.to_csv("figures/fig1b.csv", index=False)
    
    plt.figure(figsize=(8, 4.5))
    plt.plot(df_out["followees_F"], df_out["latency_med_ms"], marker="o", label="Latence client médiane (ms)")
    plt.plot(df_out["followees_F"], df_out["server_med_ms"], marker="s", linestyle="--", label="Server-Timing médian (ms)")
    plt.xlabel("Nombre d'abonnements F (followees)")
    plt.ylabel("Temps médian (ms)")
    plt.title("Fig 1b — Temps de réponse médian selon F (1 client)")
    plt.grid(True, ls=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/fig1b.png", dpi=150)
    plt.close()

def parse_part2():
    rows = []
    for path in glob.glob("raw/*_[nN]*_[cC]*.csv"):
        match = re.search(r"_[nN](\d+)_[cC](\d+)\.csv$", path)
        if match:
            n, c = int(match.group(1)), int(match.group(2))
            m = compute_metrics(path)
            rows.append({"instances_N": n, "concurrency_C": c, **m})
    return pd.DataFrame(rows).sort_values(["instances_N", "concurrency_C"])

def build_fig2a():
    #Débit en fonction de C pour N=1, 2, 4
    df_out = parse_part2()
    df_out.to_csv("figures/fig2a.csv", index=False)
    
    plt.figure(figsize=(8, 4.5))
    for n in sorted(df_out["instances_N"].unique()):
        sub = df_out[df_out["instances_N"] == n]
        plt.plot(sub["concurrency_C"], sub["throughput_req_s"], marker="o", label=f"N = {n} instance(s)")
    plt.xlabel("Utilisateurs simultanés C")
    plt.ylabel("Débit (req/s)")
    plt.title("Fig 2a — Débit en fonction de la concurrence (N = 1, 2, 4)")
    plt.grid(True, ls=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/fig2a.png", dpi=150)
    plt.close()

def build_fig2b():
    #Latence médiane en fonction de C pour N=1, 2, 4 (Loi de Little)
    df_out = parse_part2()
    df_out.to_csv("figures/fig2b.csv", index=False)
    
    plt.figure(figsize=(8, 4.5))
    for n in sorted(df_out["instances_N"].unique()):
        sub = df_out[df_out["instances_N"] == n]
        plt.plot(sub["concurrency_C"], sub["latency_med_ms"], marker="o", label=f"N = {n} instance(s)")
    plt.xlabel("Utilisateurs simultanés C")
    plt.ylabel("Latence médiane (ms)")
    plt.title("Fig 2b — Latence médiane en fonction de la concurrence (N = 1, 2, 4)")
    plt.grid(True, ls=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/fig2b.png", dpi=150)
    plt.close()

def build_fig3():
    #Comparaison Avant (N=1) vs Après optimisation (Partie 3)
    df_before = parse_part2()
    df_before = df_before[df_before["instances_N"] == 1].copy()
    df_before["version"] = "Avant (N=1)"
    
    rows_after = []
    for path in glob.glob("raw/*opti*_[cC]*.csv"):
        match = re.search(r"_[cC](\d+)\.csv$", path)
        if match:
            c = int(match.group(1))
            m = compute_metrics(path)
            rows_after.append({"version": "Après (opti)", "instances_N": 1, "concurrency_C": c, **m})
            
    df_out = pd.concat([df_before, pd.DataFrame(rows_after)], ignore_index=True)
    df_out.to_csv("figures/fig3.csv", index=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ver in df_out["version"].unique():
        sub = df_out[df_out["version"] == ver].sort_values("concurrency_C")
        axes[0].plot(sub["concurrency_C"], sub["throughput_req_s"], marker="o", label=ver)
        axes[1].plot(sub["concurrency_C"], sub["latency_med_ms"], marker="o", label=ver)
    axes[0].set_title("Débit (req/s)")
    axes[0].set_xlabel("Concurrence C")
    axes[0].set_ylabel("Débit (req/s)")
    axes[1].set_title("Latence médiane (ms)")
    axes[1].set_xlabel("Concurrence C")
    axes[1].set_ylabel("Latence médiane (ms)")
    for ax in axes:
        ax.grid(True, ls=":")
        ax.legend()
    fig.suptitle("Fig 3 — Comparaison Avant / Après optimisation")
    plt.tight_layout()
    plt.savefig("figures/fig3.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="all", choices=["fig1a", "fig1b", "fig2a", "fig2b", "fig3", "all"])
    args = parser.parse_args()
    
    if args.target in ("fig1a", "all"): build_fig1a()
    if args.target in ("fig1b", "all"): build_fig1b()
    if args.target in ("fig2a", "all"): build_fig2a()
    if args.target in ("fig2b", "all"): build_fig2b()
    if args.target in ("fig3", "all") and glob.glob("raw/*opti*"): build_fig3()