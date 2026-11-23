import glob

# Détection automatique des fichiers bruts déjà présents dans raw/
RAW_P1_UP = glob.glob("raw/*_u*.csv") + glob.glob("raw/*_p[0-9]*.csv")
RAW_P1_F  = glob.glob("raw/*_f*.csv")
RAW_P2    = glob.glob("raw/*_[nN]*_[cC]*.csv")
RAW_P3    = glob.glob("raw/*opti*_[cC]*.csv")

# Cibles finales : fig1a, fig1b, fig2a, fig2b (et fig3 si les CSV de la partie 3 existent)
TARGETS = [
    "figures/fig1a.csv", "figures/fig1a.png",
    "figures/fig1b.csv", "figures/fig1b.png",
    "figures/fig2a.csv", "figures/fig2a.png",
    "figures/fig2b.csv", "figures/fig2b.png",
]
if RAW_P3:
    TARGETS += ["figures/fig3.csv", "figures/fig3.png"]

rule all:
    input:
        TARGETS

rule fig1a:
    input:
        RAW_P1_UP,
        script="bench/analyze.py"
    output:
        "figures/fig1a.csv",
        "figures/fig1a.png"
    shell:
        "python {input.script} --target fig1a"

rule fig1b:
    input:
        RAW_P1_F,
        script="bench/analyze.py"
    output:
        "figures/fig1b.csv",
        "figures/fig1b.png"
    shell:
        "python {input.script} --target fig1b"

rule fig2a:
    input:
        RAW_P2,
        script="bench/analyze.py"
    output:
        "figures/fig2a.csv",
        "figures/fig2a.png"
    shell:
        "python {input.script} --target fig2a"

rule fig2b:
    input:
        RAW_P2,
        script="bench/analyze.py"
    output:
        "figures/fig2b.csv",
        "figures/fig2b.png"
    shell:
        "python {input.script} --target fig2b"

rule fig3:
    input:
        RAW_P2,
        RAW_P3,
        script="bench/analyze.py"
    output:
        "figures/fig3.csv",
        "figures/fig3.png"
    shell:
        "python {input.script} --target fig3"